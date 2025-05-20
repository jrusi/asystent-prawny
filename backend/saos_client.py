import requests
import json
from fastapi import HTTPException, status
from typing import List, Dict, Any
from datetime import datetime
import time
import random

class SAOSClient:
    """Klient do komunikacji z API Systemem Analizy Orzeczeń Sądowych (SAOS)"""
    
    def __init__(self):
        """Inicjalizacja klienta SAOS"""
        self.base_url = "https://www.saos.org.pl/api"
        self.api_version = "v1"
        self.search_endpoint = f"{self.base_url}/{self.api_version}/search/judgments"
        self.judgment_endpoint = f"{self.base_url}/{self.api_version}/judgments"
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    
    def search_judgments(self, keywords: List[str], page_size: int = 10) -> List[Dict[str, Any]]:
        """
        Wyszukiwanie orzeczeń w SAOS
        
        Args:
            keywords: Lista słów kluczowych do wyszukiwania
            page_size: Liczba wyników na stronie
        
        Returns:
            Lista znalezionych orzeczeń
        """
        # W rzeczywistej implementacji, tutaj byłoby odpytanie API SAOS
        # Poniżej mamy implementację symulacyjną, która zwraca przykładowe dane
        
        # Symulacja opóźnienia wyszukiwania
        time.sleep(random.uniform(0.5, 1.5))
        
        # Przykładowe orzeczenia
        example_judgments = [
            {
                "court_name": "Sąd Najwyższy",
                "case_number": "III CZP 36/19",
                "judgment_date": datetime(2020, 1, 15),
                "content": """Sąd Najwyższy w składzie: (...)

TEZA
Sądem właściwym do nadania klauzuli wykonalności aktowi notarialnemu, w którym dłużnik poddał się egzekucji w trybie art. 777 § 1 pkt 5 k.p.c. i który spełnia wszystkie wymagania przewidziane tym przepisem, jest sąd rejonowy ogólnej właściwości dłużnika (art. 781 § 1 k.p.c.).

UZASADNIENIE
(...)
                """,
                "saos_id": "judgment-12345"
            },
            {
                "court_name": "Naczelny Sąd Administracyjny",
                "case_number": "II OSK: 1257/19",
                "judgment_date": datetime(2020, 3, 5),
                "content": """Naczelny Sąd Administracyjny w składzie: (...)

UZASADNIENIE
Zaskarżonym wyrokiem z dnia 6 lutego 2019 r. Wojewódzki Sąd Administracyjny w Warszawie oddalił skargę B.L. na decyzję Samorządowego Kolegium Odwoławczego w W. z dnia 12 lipca 2018 r. nr [...] w przedmiocie odmowy stwierdzenia nieważności decyzji.
(...)
                """,
                "saos_id": "judgment-67890"
            },
            {
                "court_name": "Sąd Apelacyjny w Warszawie",
                "case_number": "V ACa 248/18",
                "judgment_date": datetime(2019, 6, 20),
                "content": """Sąd Apelacyjny w Warszawie V Wydział Cywilny w składzie: (...)

TEZA
Przyczyną spadku wartości nieruchomości obciążonej służebnością przesyłu są ograniczenia, które właściciel zobowiązany jest znosić w związku z korzystaniem z nieruchomości przez uprawniony podmiot oraz te, które wiążą się z posadowieniem urządzeń na nieruchomości.

UZASADNIENIE
(...)
                """,
                "saos_id": "judgment-24680"
            },
            {
                "court_name": "Wojewódzki Sąd Administracyjny w Krakowie",
                "case_number": "I SA/Kr 1234/19",
                "judgment_date": datetime(2020, 2, 10),
                "content": """Wojewódzki Sąd Administracyjny w Krakowie w składzie: (...)

UZASADNIENIE
Decyzją z dnia [...] Dyrektor Izby Administracji Skarbowej w K., po rozpatrzeniu odwołania skarżącej, utrzymał w mocy decyzję Naczelnika Urzędu Skarbowego w T. z dnia [...] określającą skarżącej zobowiązanie podatkowe w podatku od towarów i usług za poszczególne miesiące 2016 r.
(...)
                """,
                "saos_id": "judgment-13579"
            }
        ]
        
        # Filtrowanie według słów kluczowych
        filtered_judgments = []
        for judgment in example_judgments:
            for keyword in keywords:
                if keyword.lower() in judgment["court_name"].lower() or \
                   keyword.lower() in judgment["case_number"].lower() or \
                   keyword.lower() in judgment["content"].lower():
                    filtered_judgments.append(judgment)
                    break
        
        # Jeśli nie znaleziono żadnych pasujących orzeczeń, zwróć wszystkie przykładowe
        if not filtered_judgments:
            return example_judgments
        
        return filtered_judgments
    
    def get_judgment_details(self, judgment_id: str) -> Dict[str, Any]:
        """
        Pobieranie szczegółów orzeczenia
        
        Args:
            judgment_id: Identyfikator orzeczenia w SAOS
        
        Returns:
            Szczegóły orzeczenia
        """
        # W rzeczywistej implementacji, tutaj byłoby odpytanie API SAOS
        # Poniżej mamy implementację symulacyjną
        
        # Symulacja opóźnienia
        time.sleep(random.uniform(0.5, 1.0))
        
        # Przykładowe szczegóły orzeczenia
        judgment_details = {
            "judgment-12345": {
                "id": "judgment-12345",
                "court_name": "Sąd Najwyższy",
                "case_number": "III CZP 36/19",
                "judgment_date": "2020-01-15",
                "judges": [
                    "Jan Kowalski",
                    "Anna Nowak",
                    "Piotr Wiśniewski"
                ],
                "content": """Sąd Najwyższy w składzie: (...)

TEZA
Sądem właściwym do nadania klauzuli wykonalności aktowi notarialnemu, w którym dłużnik poddał się egzekucji w trybie art. 777 § 1 pkt 5 k.p.c. i który spełnia wszystkie wymagania przewidziane tym przepisem, jest sąd rejonowy ogólnej właściwości dłużnika (art. 781 § 1 k.p.c.).

UZASADNIENIE
(...)
                """,
                "keywords": [
                    "klauzula wykonalności",
                    "akt notarialny",
                    "właściwość sądu"
                ]
            },
            "judgment-67890": {
                "id": "judgment-67890",
                "court_name": "Naczelny Sąd Administracyjny",
                "case_number": "II OSK: 1257/19",
                "judgment_date": "2020-03-05",
                "judges": [
                    "Maria Kowalczyk",
                    "Tomasz Nowicki",
                    "Agnieszka Dąbrowska"
                ],
                "content": """Naczelny Sąd Administracyjny w składzie: (...)

UZASADNIENIE
Zaskarżonym wyrokiem z dnia 6 lutego 2019 r. Wojewódzki Sąd Administracyjny w Warszawie oddalił skargę B.L. na decyzję Samorządowego Kolegium Odwoławczego w W. z dnia 12 lipca 2018 r. nr [...] w przedmiocie odmowy stwierdzenia nieważności decyzji.
(...)
                """,
                "keywords": [
                    "skarga kasacyjna",
                    "postępowanie administracyjne",
                    "stwierdzenie nieważności"
                ]
            }
        }
        
        if judgment_id in judgment_details:
            return judgment_details[judgment_id]
        
        # Jeśli nie znaleziono orzeczenia o podanym ID, zwróć błąd
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Nie znaleziono orzeczenia o identyfikatorze {judgment_id}"
        )
    
    def get_recent_judgments(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Pobieranie najnowszych orzeczeń
        
        Args:
            limit: Maksymalna liczba orzeczeń do pobrania
        
        Returns:
            Lista najnowszych orzeczeń
        """
        # Symulacja opóźnienia
        time.sleep(random.uniform(0.5, 1.0))
        
        # Przykładowe najnowsze orzeczenia
        recent_judgments = [
            {
                "court_name": "Sąd Najwyższy",
                "case_number": "III CZP 42/20",
                "judgment_date": datetime(2020, 5, 10),
                "content": "Skrócona treść orzeczenia...",
                "saos_id": "judgment-54321"
            },
            {
                "court_name": "Naczelny Sąd Administracyjny",
                "case_number": "II OSK: 3265/19",
                "judgment_date": datetime(2020, 5, 8),
                "content": "Skrócona treść orzeczenia...",
                "saos_id": "judgment-98765"
            },
            {
                "court_name": "Sąd Apelacyjny w Warszawie",
                "case_number": "V ACa 537/19",
                "judgment_date": datetime(2020, 5, 5),
                "content": "Skrócona treść orzeczenia...",
                "saos_id": "judgment-24681"
            }
        ]
        
        return recent_judgments[:limit]
