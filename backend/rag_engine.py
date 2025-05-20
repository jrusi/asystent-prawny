import httpx
import logging
from typing import List, Dict, Any, Optional, Union
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

class SAOSClient:
    """
    Klient do komunikacji z API SAOS (System Analizy Orzeczeń Sądowych)
    """
    
    BASE_URL = "https://www.saos.org.pl/api"
    SEARCH_URL = f"{BASE_URL}/search/judgments"
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def search_judgments(self, 
                         query: str = None, 
                         case_number: str = None,
                         judge_name: str = None,
                         court_type: str = None,  # "COMMON", "SUPREME", "CONSTITUTIONAL_TRIBUNAL"
                         from_date: str = None,   # Format: "YYYY-MM-DD"
                         to_date: str = None,     # Format: "YYYY-MM-DD"
                         keywords: List[str] = None,
                         legal_bases: List[str] = None,
                         page_size: int = 20,
                         page_number: int = 0) -> Dict[str, Any]:
        """
        Wyszukuje orzeczenia sądowe w SAOS na podstawie podanych kryteriów.
        
        Args:
            query: Ogólne zapytanie
            case_number: Numer sprawy
            judge_name: Nazwisko sędziego
            court_type: Typ sądu (COMMON, SUPREME, CONSTITUTIONAL_TRIBUNAL)
            from_date: Data od (YYYY-MM-DD)
            to_date: Data do (YYYY-MM-DD)
            keywords: Lista słów kluczowych
            legal_bases: Lista podstaw prawnych
            page_size: Liczba wyników na stronę
            page_number: Numer strony wyników
            
        Returns:
            Dane odpowiedzi z API SAOS
        """
        params = {
            "pageSize": page_size,
            "pageNumber": page_number,
            "sortingField": "JUDGMENT_DATE",
            "sortingDirection": "DESC"
        }
        
        if query:
            params["all"] = query
            
        if case_number:
            params["caseNumber"] = case_number
            
        if judge_name:
            params["judgeName"] = judge_name
            
        if court_type:
            params["courtType"] = court_type
            
        if from_date:
            params["judgmentDateFrom"] = from_date
            
        if to_date:
            params["judgmentDateTo"] = to_date
            
        if keywords:
            for idx, keyword in enumerate(keywords):
                params[f"keyword[{idx}]"] = keyword
                
        if legal_bases:
            for idx, legal_base in enumerate(legal_bases):
                params[f"legalBase[{idx}]"] = legal_base
        
        try:
            response = await self.client.get(self.SEARCH_URL, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e}")
            return {"items": [], "totalResults": 0}
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            return {"items": [], "totalResults": 0}
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return {"items": [], "totalResults": 0}
    
    async def get_judgment_details(self, judgment_id: int) -> Optional[Dict[str, Any]]:
        """
        Pobiera szczegóły orzeczenia sądowego na podstawie jego ID.
        
        Args:
            judgment_id: Identyfikator orzeczenia
            
        Returns:
            Słownik z danymi orzeczenia lub None w przypadku błędu
        """
        try:
            response = await self.client.get(f"{self.BASE_URL}/judgments/{judgment_id}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e}")
            return None
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return None
    
    async def find_similar_judgments(self, 
                              case_text: str, 
                              keywords: List[str] = None, 
                              max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Wyszukuje orzeczenia podobne do podanego tekstu sprawy.
        
        Args:
            case_text: Tekst sprawy
            keywords: Lista słów kluczowych
            max_results: Maksymalna liczba wyników
            
        Returns:
            Lista podobnych orzeczeń
        """
        # Ekstrakcja słów kluczowych z tekstu sprawy
        extracted_keywords = await self._extract_keywords_from_text(case_text)
        
        # Połączenie z dostarczonymi słowami kluczowymi
        all_keywords = extracted_keywords
        if keywords:
            all_keywords.extend(keywords)
            # Usuń duplikaty
            all_keywords = list(set(all_keywords))
        
        # Wyszukiwanie orzeczeń na podstawie słów kluczowych
        search_results = await self.search_judgments(
            keywords=all_keywords,
            page_size=max_results
        )
        
        return search_results.get("items", [])
    
    async def _extract_keywords_from_text(self, text: str) -> List[str]:
        """
        Ekstrahuje słowa kluczowe z tekstu.
        
        Args:
            text: Tekst do analizy
            
        Returns:
            Lista słów kluczowych
        """
        # Uproszczona implementacja - w rzeczywistości można użyć bardziej 
        # zaawansowanych algorytmów NLP
        import re
        from collections import Counter
        
        # Lista stop words dla języka polskiego (skrócona)
        stop_words = set(['a', 'aby', 'ale', 'bez', 'bo', 'być', 'czy', 'dla', 'do', 
                        'gdy', 'gdzie', 'i', 'jak', 'jest', 'jeszcze', 'jeśli', 
                        'lub', 'ma', 'nie', 'o', 'od', 'po', 'pod', 'przy', 'się', 
                        'tylko', 'w', 'we', 'z', 'za', 'ze'])
        
        # Zamieniamy na małe litery i usuwamy znaki specjalne
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        
        # Dzielimy na słowa
        words = text.split()
        
        # Usuwamy stop words i krótkie słowa (mniej niż 3 znaki)
        words = [word for word in words if word not in stop_words and len(word) > 3]
        
        # Liczymy częstość występowania słów
        word_count = Counter(words)
        
        # Zwracamy najczęściej występujące słowa jako słowa kluczowe (max 10)
        return [word for word, count in word_count.most_common(10)]
    
    async def extract_legal_bases(self, text: str) -> List[str]:
        """
        Ekstrahuje podstawy prawne z tekstu dokumentu.
        
        Args:
            text: Tekst dokumentu
            
        Returns:
            Lista znalezionych podstaw prawnych
        """
        # Uproszczona implementacja - w rzeczywistości należy użyć bardziej 
        # zaawansowanych technik NLP lub wyrażeń regularnych
        
        # Przykładowy wzorzec dla polskich podstaw prawnych
        import re
        
        patterns = [
            # Wzorzec dla ustaw
            r'ustaw[a-zęóąśłżźćń]* z dnia \d{1,2} [a-zęóąśłżźćń]+ \d{4} r\. [^\.]+',
            # Wzorzec dla artykułów
            r'art\.\s*\d+\s*(?:ust\.\s*\d+\s*)?(?:pkt\.\s*\d+\s*)?[^\.]+',
            # Wzorzec dla paragrafów
            r'§\s*\d+\s*(?:ust\.\s*\d+\s*)?(?:pkt\.\s*\d+\s*)?[^\.]+',
            # Wzorzec dla kodeksów
            r'kodeks[a-zęóąśłżźćń]*\s+[a-zęóąśłżźćń]+\s*(?:z dnia \d{1,2} [a-zęóąśłżźćń]+ \d{4} r\.)?',
        ]
        
        legal_bases = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            legal_bases.extend(matches)
        
        # Unikalne podstawy prawne
        legal_bases = list(set(legal_bases))
        
        return legal_bases
    
    async def get_court_info(self, court_id: int) -> Optional[Dict[str, Any]]:
        """
        Pobiera informacje o sądzie na podstawie ID.
        
        Args:
            court_id: ID sądu
            
        Returns:
            Dane o sądzie lub None w przypadku błędu
        """
        try:
            response = await self.client.get(f"{self.BASE_URL}/courts/{court_id}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting court info: {e}")
            return None
    
    async def get_division_info(self, division_id: int, court_type: str) -> Optional[Dict[str, Any]]:
        """
        Pobiera informacje o wydziale sądu.
        
        Args:
            division_id: ID wydziału
            court_type: Typ sądu ("CC" dla sądów powszechnych, "SC" dla Sądu Najwyższego)
            
        Returns:
            Dane o wydziale lub None w przypadku błędu
        """
        try:
            endpoint = f"{self.BASE_URL}/ccDivisions/{division_id}" if court_type == "CC" else f"{self.BASE_URL}/scDivisions/{division_id}"
            response = await self.client.get(endpoint)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting division info: {e}")
            return None
