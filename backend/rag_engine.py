from typing import List, Dict, Any, Tuple
import os
import json
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import openai

class RAGEngine:
    """Silnik odpowiadający na pytania używając Retrieval Augmented Generation"""
    
    def __init__(self, elasticsearch_client):
        """
        Inicjalizacja silnika RAG
        
        Args:
            elasticsearch_client: Klient Elasticsearch do wyszukiwania dokumentów
        """
        self.elasticsearch_client = elasticsearch_client
        
        # Inicjalizacja klienta OpenAI
        openai.api_key = os.getenv("OPENAI_API_KEY", "sk-test-key-replace-in-production")
        
        # Utworzenie łańcucha LLM
        self.llm = OpenAI(temperature=0.2)
        
        self.prompt_template = PromptTemplate(
            input_variables=["question", "context"],
            template="""
            Odpowiedz na poniższe pytanie opierając się na dostarczonym kontekście. 
            Jeśli informacja nie znajduje się w kontekście, powiedz, że nie wiesz lub że informacja nie jest zawarta w kontekście.
            Odpowiedź powinna być szczegółowa, w języku polskim i zgodna z polskim prawem.
            
            Kontekst:
            {context}
            
            Pytanie: {question}
            
            Odpowiedź:
            """
        )
        
        self.qa_chain = LLMChain(llm=self.llm, prompt=self.prompt_template)
    
    def generate_answer(self, question: str, search_results: List[Dict[str, Any]]) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Generowanie odpowiedzi na pytanie na podstawie wyników wyszukiwania
        
        Args:
            question: Pytanie zadane przez użytkownika
            search_results: Wyniki wyszukiwania z Elasticsearch
        
        Returns:
            Tuple zawierająca odpowiedź oraz listę źródeł
        """
        # Przygotowanie kontekstu na podstawie wyników wyszukiwania
        context = self._prepare_context(search_results)
        
        # Generowanie odpowiedzi
        try:
            answer = self.qa_chain.run({"question": question, "context": context})
        except Exception as e:
            print(f"Błąd podczas generowania odpowiedzi: {e}")
            # W przypadku błędu, zwróć prostą odpowiedź
            answer = "Przepraszam, nie mogę wygenerować odpowiedzi w tej chwili."
        
        # Przygotowanie listy źródeł
        sources = self._prepare_sources(search_results)
        
        return answer, sources
    
    def _prepare_context(self, search_results: List[Dict[str, Any]]) -> str:
        """
        Przygotowanie kontekstu na podstawie wyników wyszukiwania
        
        Args:
            search_results: Wyniki wyszukiwania z Elasticsearch
        
        Returns:
            Kontekst do wykorzystania w zapytaniu do LLM
        """
        context_parts = []
        
        for result in search_results:
            source = result["source"]
            content = source.get("content", "")
            title = source.get("title", "")
            source_type = source.get("type", "dokument")
            
            # Dodanie informacji o źródle
            if source_type == "legal_act":
                source_info = f"Akt prawny: {title}, {source.get('publication', '')}"
            elif source_type == "judgment":
                source_info = f"Orzeczenie: {source.get('court_name', '')}, {source.get('case_number', '')}, {source.get('judgment_date', '')}"
            else:
                source_info = f"Dokument: {title}"
            
            # Skrócenie zawartości, jeśli jest za długa
            max_content_length = 2000  # Maksymalna długość zawartości
            if len(content) > max_content_length:
                content = content[:max_content_length] + "..."
            
            # Dodanie do kontekstu
            context_parts.append(f"{source_info}\n{content}\n")
        
        # Połączenie części kontekstu
        return "\n\n".join(context_parts)
    
    def _prepare_sources(self, search_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Przygotowanie listy źródeł na podstawie wyników wyszukiwania
        
        Args:
            search_results: Wyniki wyszukiwania z Elasticsearch
        
        Returns:
            Lista źródeł
        """
        sources = []
        
        for result in search_results:
            source = result["source"]
            source_type = source.get("type", "dokument")
            
            # Przygotowanie informacji o źródle
            source_info = {
                "score": result["score"],
                "type": source_type
            }
            
            # Dodanie specyficznych informacji w zależności od typu źródła
            if source_type == "legal_act":
                source_info.update({
                    "title": source.get("title", ""),
                    "publication": source.get("publication", ""),
                    "year": source.get("year", "")
                })
            elif source_type == "judgment":
                source_info.update({
                    "court_name": source.get("court_name", ""),
                    "case_number": source.get("case_number", ""),
                    "judgment_date": source.get("judgment_date", "")
                })
            else:
                source_info.update({
                    "filename": source.get("filename", ""),
                    "document_type": source.get("document_type", "")
                })
            
            sources.append(source_info)
        
        return sources
