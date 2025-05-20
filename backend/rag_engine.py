from typing import List, Dict, Any, Tuple
import os
import json
import openai

class RAGEngine:
    """Silnik do odpowiadania na pytania używając Retrieval Augmented Generation"""
    
    def __init__(self):
        """Inicjalizacja silnika RAG"""
        # Ustawienie klucza API dla OpenAI
        openai.api_key = os.getenv("OPENAI_API_KEY", "your-key-here")
    
    def generate_answer(self, question: str, context: List[Dict[str, Any]]) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Generowanie odpowiedzi na pytanie na podstawie dostępnego kontekstu
        
        Args:
            question: Pytanie zadane przez użytkownika
            context: Lista dokumentów stanowiących kontekst
        
        Returns:
            Tuple zawierająca odpowiedź oraz listę źródeł
        """
        # Konwersja kontekstu do tekstu
        context_text = self._prepare_context(context)
        
        # Utworzenie promptu
        prompt = f"""
        Odpowiedz na poniższe pytanie opierając się na dostarczonym kontekście. 
        Jeśli informacja nie znajduje się w kontekście, powiedz, że nie wiesz lub że informacja nie jest zawarta w kontekście.
        Odpowiedź powinna być szczegółowa, w języku polskim i zgodna z polskim prawem.
        
        Kontekst:
        {context_text}
        
        Pytanie: {question}
        
        Odpowiedź:
        """
        
        # Generowanie odpowiedzi przy użyciu OpenAI API
        try:
            response = openai.Completion.create(
                engine="gpt-3.5-turbo-instruct",
                prompt=prompt,
                max_tokens=500,
                temperature=0.2
            )
            
            answer = response.choices[0].text.strip()
        except Exception as e:
            print(f"Błąd podczas generowania odpowiedzi: {e}")
            answer = "Przepraszam, nie mogę wygenerować odpowiedzi w tej chwili."
        
        # Przygotowanie listy źródeł
        sources = self._prepare_sources(context)
        
        return answer, sources
    
    def _prepare_context(self, context: List[Dict[str, Any]]) -> str:
        """Przygotowanie kontekstu do zapytania"""
        context_parts = []
        
        for doc in context:
            # Dostosuj tę funkcję do struktury Twoich dokumentów
            title = doc.get("title", "Brak tytułu")
            content = doc.get("content", "")
            source_type = doc.get("type", "dokument")
            
            context_parts.append(f"[{source_type.upper()}] {title}\n{content}\n")
        
        return "\n\n".join(context_parts)
    
    def _prepare_sources(self, context: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Przygotowanie listy źródeł"""
        sources = []
        
        for doc in context:
            source = {
                "title": doc.get("title", "Brak tytułu"),
                "type": doc.get("type", "dokument")
            }
            
            # Dodanie dodatkowych informacji w zależności od typu dokumentu
            if doc.get("type") == "legal_act":
                source["publication"] = doc.get("publication", "")
            elif doc.get("type") == "judgment":
                source["court"] = doc.get("court_name", "")
                source["case_number"] = doc.get("case_number", "")
            
            sources.append(source)
        
        return sources
