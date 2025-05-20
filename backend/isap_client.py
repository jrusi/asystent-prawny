import requests
from bs4 import BeautifulSoup
import re
from fastapi import HTTPException, status
from typing import List, Dict, Any
import time
import random

class ISAPClient:
    """Klient do komunikacji z Internetowym Systemem Aktów Prawnych (ISAP)"""
    
    def __init__(self):
        """Inicjalizacja klienta ISAP"""
        self.base_url = "https://isap.sejm.gov.pl"
        self.search_url = f"{self.base_url}/isap.nsf/search.xsp"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "pl,en-US;q=0.7,en;q=0.3",
        }
    
    def search_acts(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """
        Wyszukiwanie aktów prawnych w ISAP
        
        Args:
            keywords: Lista słów kluczowych do wyszukiwania
        
        Returns:
            Lista znalezionych aktów prawnych
        """
        # W rzeczywistej implementacji tutaj byłoby wyszukiwanie przez ISAP API
        # lub scraping strony wyszukiwania ISAP
        # Poniżej mamy implementację symulacyjną, która zwraca przykładowe dane
        
        # Symulacja opóźnienia wyszukiwania
        time.sleep(random.uniform(0.5, 1.5))
        
        # Przykładowe akty prawne
        example_acts = [
            {
                "title": "Ustawa z dnia 17 listopada 1964 r. - Kodeks postępowania cywilnego",
                "isap_id": "WDU19640430296",
                "publication": "Dz.U. 1964 nr 43 poz. 296",
                "year": 1964,
                "content": "Art. 1. § 1. Kodeks postępowania cywilnego normuje postępowanie sądowe w sprawach ze stosunków z zakresu prawa cywilnego, rodzinnego i opiekuńczego oraz prawa pracy, jak również w sprawach z zakresu ubezpieczeń społecznych oraz w innych sprawach, do których przepisy tego Kodeksu stosuje się z mocy ustaw szczególnych (sprawy cywilne)."
            },
            {
                "title": "Ustawa z dnia 23 kwietnia 1964 r. - Kodeks cywilny",
                "isap_id": "WDU19640160093",
                "publication": "Dz.U. 1964 nr 16 poz. 93",
                "year": 1964,
                "content": "Art. 1. Kodeks niniejszy reguluje stosunki cywilnoprawne między osobami fizycznymi i osobami prawnymi."
            },
            {
                "title": "Ustawa z dnia 6 czerwca 1997 r. - Kodeks karny",
                "isap_id": "WDU19970880553",
                "publication": "Dz.U. 1997 nr 88 poz. 553",
                "year": 1997,
                "content": "Art. 1. § 1. Odpowiedzialności karnej podlega ten tylko, kto popełnia czyn zabroniony pod groźbą kary przez ustawę obowiązującą w czasie jego popełnienia."
            },
            {
                "title": "Ustawa z dnia 6 czerwca 1997 r. - Kodeks postępowania karnego",
                "isap_id": "WDU19970890555",
                "publication": "Dz.U. 1997 nr 89 poz. 555",
                "year": 1997,
                "content": "Art. 1. § 1. Postępowanie karne w sprawach należących do właściwości sądów toczy się według przepisów niniejszego kodeksu."
            },
            {
                "title": "Ustawa z dnia 26 czerwca 1974 r. - Kodeks pracy",
                "isap_id": "WDU19740240141",
                "publication": "Dz.U. 1974 nr 24 poz. 141",
                "year": 1974,
                "content": "Art. 1. Kodeks pracy określa prawa i obowiązki pracowników i pracodawców."
            }
        ]
        
        # Filtrowanie według słów kluczowych
        filtered_acts = []
        for act in example_acts:
            for keyword in keywords:
                if keyword.lower() in act["title"].lower() or keyword.lower() in act["content"].lower():
                    filtered_acts.append(act)
                    break
        
        # Jeśli nie znaleziono żadnych pasujących aktów, zwróć wszystkie przykładowe
        if not filtered_acts:
            return example_acts
        
        return filtered_acts
    
    def get_act_content(self, isap_id: str) -> str:
        """
        Pobieranie treści aktu prawnego
        
        Args:
            isap_id: Identyfikator aktu prawnego w ISAP
        
        Returns:
            Treść aktu prawnego
        """
        # W rzeczywistej implementacji tutaj byłoby pobieranie treści przez ISAP API
        # lub scraping strony z treścią aktu prawnego
        # Poniżej mamy implementację symulacyjną
        
        # Symulacja opóźnienia
        time.sleep(random.uniform(1.0, 2.0))
        
        # Przykładowa treść dla wybranych aktów
        example_contents = {
            "WDU19640430296": """Ustawa z dnia 17 listopada 1964 r. - Kodeks postępowania cywilnego

TYTUŁ WSTĘPNY. Przepisy ogólne

Art. 1. § 1. Kodeks postępowania cywilnego normuje postępowanie sądowe w sprawach ze stosunków z zakresu prawa cywilnego, rodzinnego i opiekuńczego oraz prawa pracy, jak również w sprawach z zakresu ubezpieczeń społecznych oraz w innych sprawach, do których przepisy tego Kodeksu stosuje się z mocy ustaw szczególnych (sprawy cywilne).
§ 2. Przepisy Kodeksu stosuje się także do postępowań w sprawach, do których przepisy innych ustaw nie stanowią inaczej.
§ 3. Nie są rozpoznawane w postępowaniu sądowym sprawy cywilne, jeżeli przepisy szczególne przekazują je do właściwości innych organów.""",
            "WDU19640160093": """Ustawa z dnia 23 kwietnia 1964 r. - Kodeks cywilny

KSIĘGA PIERWSZA. CZĘŚĆ OGÓLNA

TYTUŁ I. Przepisy wstępne

Art. 1. Kodeks niniejszy reguluje stosunki cywilnoprawne między osobami fizycznymi i osobami prawnymi.

Art. 2. Jeżeli ustawa nie stanowi inaczej, do osoby fizycznej wykonującej działalność gospodarczą stosuje się przepisy Kodeksu dotyczące przedsiębiorców.""",
        }
        
        # Jeśli znamy treść aktu, zwróć ją
        if isap_id in example_contents:
            return example_contents[isap_id]
        
        # W przeciwnym przypadku zwróć ogólną informację
        return f"Treść aktu prawnego o identyfikatorze {isap_id} w systemie ISAP."
    
    def get_recent_acts(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Pobieranie najnowszych aktów prawnych
        
        Args:
            limit: Maksymalna liczba aktów do pobrania
        
        Returns:
            Lista najnowszych aktów prawnych
        """
        # W rzeczywistej implementacji tutaj byłoby pobieranie najnowszych aktów przez ISAP API
        # lub scraping strony z najnowszymi aktami
        # Poniżej mamy implementację symulacyjną
        
        # Symulacja opóźnienia
        time.sleep(random.uniform(0.5, 1.0))
        
        # Przykładowe najnowsze akty
        recent_acts = [
            {
                "title": "Ustawa z dnia 14 maja 2020 r. o zmianie niektórych ustaw w zakresie działań osłonowych w związku z rozprzestrzenianiem się wirusa SARS-CoV-2",
                "isap_id": "WDU20200000875",
                "publication": "Dz.U. 2020 poz. 875",
                "year": 2020,
                "content": "Art. 1. W ustawie z dnia 31 stycznia 1959 r. o cmentarzach i chowaniu zmarłych (Dz. U. z 2019 r. poz. 1473) wprowadza się następujące zmiany: (...)"
            },
            {
                "title": "Ustawa z dnia 14 maja 2020 r. o zmianie ustawy o świadczeniach opieki zdrowotnej finansowanych ze środków publicznych oraz niektórych innych ustaw",
                "isap_id": "WDU20200000945",
                "publication": "Dz.U. 2020 poz. 945",
                "year": 2020,
                "content": "Art. 1. W ustawie z dnia 27 sierpnia 2004 r. o świadczeniach opieki zdrowotnej finansowanych ze środków publicznych (Dz. U. z 2019 r. poz. 1373, z późn. zm.) wprowadza się następujące zmiany: (...)"
            }
        ]
        
        return recent_acts[:limit]
