import httpx
import os
import logging
from urllib.parse import urlencode
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class ISAPClient:
    """
    Klient do pobierania aktów prawnych z ISAP (Internetowy System Aktów Prawnych)
    """
    
    BASE_URL = "https://isap.sejm.gov.pl/isap.nsf"
    SEARCH_URL = f"{BASE_URL}/Search.xsp"
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def search_acts(self, query: str, year: Optional[int] = None, 
                     document_type: Optional[str] = None, 
                     max_results: int = 20) -> List[Dict[str, Any]]:
        """
        Wyszukuje akty prawne w ISAP na podstawie podanych kryteriów.
        
        Args:
            query: Słowa kluczowe do wyszukania
            year: Opcjonalnie rok publikacji
            document_type: Opcjonalnie typ dokumentu (np. "ustawa", "rozporządzenie")
            max_results: Maksymalna liczba wyników
            
        Returns:
            Lista słowników zawierających informacje o aktach prawnych
        """
        params = {
            "query": query,
            "max_results": max_results
        }
        
        if year:
            params["year"] = year
            
        if document_type:
            params["document_type"] = document_type
        
        try:
            # Wykonanie zapytania do ISAP
            response = await self.client.get(
                self.SEARCH_URL,
                params=params
            )
            response.raise_for_status()
            
            # Parsowanie HTML - w rzeczywistej implementacji należy dostosować 
            # do aktualnej struktury strony ISAP
            soup = BeautifulSoup(response.text, 'html.parser')
            
            results = []
            for item in soup.select('.search-result-item'):  # Selektor CSS trzeba dostosować
                act = {
                    'id': item.get('data-id', ''),
                    'title': item.select_one('.title').text.strip(),
                    'publication_date': item.select_one('.date').text.strip(),
                    'document_type': item.select_one('.type').text.strip(),
                    'url': self.BASE_URL + item.select_one('a')['href']
                }
                results.append(act)
            
            return results[:max_results]
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e}")
            return []
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return []
    
    async def get_act_details(self, act_id: str) -> Optional[Dict[str, Any]]:
        """
        Pobiera szczegóły aktu prawnego na podstawie jego ID.
        
        Args:
            act_id: Identyfikator aktu prawnego
            
        Returns:
            Słownik zawierający szczegóły aktu prawnego lub None w przypadku błędu
        """
        try:
            response = await self.client.get(
                f"{self.BASE_URL}/DocDetails.xsp",
                params={"id": act_id}
            )
            response.raise_for_status()
            
            # Parsowanie HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Pobieranie metadanych - selektory trzeba dostosować do struktury strony
            details = {
                'id': act_id,
                'title': soup.select_one('.title').text.strip(),
                'publication_date': soup.select_one('.date').text.strip(),
                'document_type': soup.select_one('.type').text.strip(),
                'text': soup.select_one('.content').text.strip(),
                'pdf_url': soup.select_one('.pdf-link')['href'],
                'amendments': [a.text.strip() for a in soup.select('.amendments li')]
            }
            
            return details
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e}")
            return None
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return None
    
    async def extract_keywords_from_document(self, document_text: str) -> List[str]:
        """
        Ekstrahuje słowa kluczowe z dokumentu, które mogą być użyte do wyszukiwania 
        odpowiednich aktów prawnych.
        
        Args:
            document_text: Tekst dokumentu
            
        Returns:
            Lista słów kluczowych
        """
        # Uproszczona implementacja - w rzeczywistości można użyć bardziej 
        # zaawansowanych algorytmów NLP
        # Przykładowo: Spacy, KeyBERT lub inne biblioteki do ekstrakcji słów kluczowych
        
        # Usuwamy znaki specjalne, dzielimy na słowa i wybieramy najczęstsze
        import re
        from collections import Counter
        
        # Lista stop words dla języka polskiego
        stop_words = set(['a', 'aby', 'ach', 'acz', 'aczkolwiek', 'aj', 'albo', 'ale', 'ależ', 
                         'ani', 'aż', 'bardziej', 'bardzo', 'bez', 'bo', 'bowiem', 'by', 
                         'byli', 'bym', 'był', 'była', 'było', 'były', 'będzie', 'będą', 
                         'cali', 'cała', 'cały', 'co', 'cokolwiek', 'coś', 'czasami', 
                         'czasem', 'czemu', 'czy', 'czyli', 'daleko', 'dla', 'dlaczego', 
                         'dlatego', 'do', 'dobrze', 'dokąd', 'dość', 'dużo', 'dwa', 
                         'dwaj', 'dwie', 'dwoje', 'dziś', 'dzisiaj', 'gdy', 'gdyby', 
                         'gdyż', 'gdzie', 'gdziekolwiek', 'gdzieś', 'go', 'i', 'ich', 
                         'ile', 'im', 'inna', 'inne', 'inny', 'innych', 'iż', 'ja', 
                         'jak', 'jakaś', 'jakby', 'jaki', 'jakichś', 'jakie', 'jakiś', 
                         'jakiż', 'jakkolwiek', 'jako', 'jakoś', 'je', 'jeden', 'jedna', 
                         'jedno', 'jednak', 'jednakże', 'jego', 'jej', 'jemu', 'jest', 
                         'jestem', 'jeszcze', 'jeśli', 'jeżeli', 'już', 'ją', 'każdy', 
                         'kiedy', 'kilka', 'kimś', 'kto', 'ktokolwiek', 'ktoś', 'która', 
                         'które', 'którego', 'której', 'który', 'których', 'którym', 
                         'którzy', 'ku', 'lat', 'lecz', 'lub', 'ma', 'mają', 'mam', 
                         'mi', 'mimo', 'między', 'mną', 'mnie', 'mogą', 'moim', 'moja', 
                         'moje', 'może', 'możliwe', 'można', 'mój', 'mu', 'musi', 'my', 
                         'na', 'nad', 'nam', 'nami', 'nas', 'nasi', 'nasz', 'nasza', 
                         'nasze', 'naszego', 'naszych', 'natomiast', 'natychmiast', 
                         'nawet', 'nią', 'nic', 'nich', 'nie', 'niech', 'niego', 'niej', 
                         'niemu', 'nigdy', 'nim', 'nimi', 'niż', 'no', 'o', 'obok', 
                         'od', 'około', 'on', 'ona', 'one', 'oni', 'ono', 'oraz', 
                         'oto', 'owszem', 'pan', 'pana', 'pani', 'po', 'pod', 'podczas', 
                         'pomimo', 'ponad', 'ponieważ', 'powinien', 'powinna', 'powinni', 
                         'powinno', 'poza', 'prawie', 'przecież', 'przed', 'przede', 
                         'przedtem', 'przez', 'przy', 'roku', 'również', 'sam', 'sama', 
                         'są', 'się', 'skąd', 'sobie', 'sobą', 'sposób', 'swoje', 'ta', 
                         'tak', 'taka', 'taki', 'takie', 'także', 'tam', 'te', 'tego', 
                         'tej', 'temu', 'ten', 'teraz', 'też', 'to', 'tobą', 'tobie', 
                         'toteż', 'trzeba', 'tu', 'tutaj', 'twoi', 'twoim', 'twoja', 
                         'twoje', 'twym', 'twój', 'ty', 'tych', 'tylko', 'tym', 'u', 
                         'w', 'wam', 'wami', 'was', 'wasz', 'wasza', 'wasze', 'we', 
                         'według', 'wiele', 'wielu', 'więc', 'więcej', 'wszyscy', 
                         'wszystkich', 'wszystkie', 'wszystkim', 'wszystko', 'wtedy', 
                         'www', 'wy', 'właśnie', 'z', 'za', 'zapewne', 'zawsze', 'ze', 
                         'zł', 'znowu', 'znów', 'został', 'żaden', 'żadna', 'żadne', 
                         'żadnych', 'że', 'żeby'])
        
        # Zamieniamy na małe litery i usuwamy znaki specjalne
        text = re.sub(r'[^\w\s]', ' ', document_text.lower())
        
        # Dzielimy na słowa
        words = text.split()
        
        # Usuwamy stop words i krótkie słowa (mniej niż 3 znaki)
        words = [word for word in words if word not in stop_words and len(word) > 3]
        
        # Liczymy częstość występowania słów
        word_count = Counter(words)
        
        # Zwracamy najczęściej występujące słowa jako słowa kluczowe (max 10)
        return [word for word, count in word_count.most_common(10)]
    
    async def download_act_pdf(self, pdf_url: str, destination_path: str) -> bool:
        """
        Pobiera PDF aktu prawnego.
        
        Args:
            pdf_url: URL do pliku PDF
            destination_path: Ścieżka, gdzie zapisać plik
            
        Returns:
            True jeśli pobieranie się powiodło, False w przeciwnym razie
        """
        try:
            response = await self.client.get(pdf_url)
            response.raise_for_status()
            
            with open(destination_path, 'wb') as f:
                f.write(response.content)
            
            return True
        except Exception as e:
            logger.error(f"Error downloading PDF: {e}")
            return False
