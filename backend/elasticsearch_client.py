from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ElasticsearchException
from fastapi import HTTPException, status

class ElasticsearchClient:
    def __init__(self, url):
        """Inicjalizacja klienta Elasticsearch"""
        self.es = Elasticsearch([url])
    
    def check_connection(self):
        """Sprawdzenie połączenia z Elasticsearch"""
        try:
            if not self.es.ping():
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Nie można połączyć się z Elasticsearch"
                )
            return True
        except ElasticsearchException as e:
            print(f"Błąd Elasticsearch: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Nie można połączyć się z Elasticsearch: {str(e)}"
            )
    
    def create_case_index(self, index_name):
        """Tworzenie indeksu dla sprawy"""
        try:
            # Sprawdzenie czy indeks już istnieje
            if not self.es.indices.exists(index=index_name):
                # Konfiguracja indeksu
                index_config = {
                    "settings": {
                        "analysis": {
                            "analyzer": {
                                "polish": {
                                    "type": "custom",
                                    "tokenizer": "standard",
                                    "filter": ["lowercase", "polish_stop", "polish_stem"]
                                }
                            },
                            "filter": {
                                "polish_stop": {
                                    "type": "stop",
                                    "stopwords": "_polish_"
                                },
                                "polish_stem": {
                                    "type": "stemmer",
                                    "language": "polish"
                                }
                            }
                        }
                    },
                    "mappings": {
                        "properties": {
                            "content": {
                                "type": "text",
                                "analyzer": "polish"
                            },
                            "title": {
                                "type": "text",
                                "analyzer": "polish"
                            },
                            "filename": {
                                "type": "text",
                                "analyzer": "polish"
                            },
                            "document_type": {
                                "type": "keyword"
                            },
                            "court_name": {
                                "type": "text",
                                "analyzer": "polish"
                            },
                            "case_number": {
                                "type": "keyword"
                            },
                            "publication": {
                                "type": "keyword"
                            },
                            "year": {
                                "type": "integer"
                            },
                            "type": {
                                "type": "keyword"
                            },
                            "timestamp": {
                                "type": "date"
                            }
                        }
                    }
                }
                
                # Utworzenie indeksu
                self.es.indices.create(index=index_name, body=index_config)
                print(f"Indeks '{index_name}' utworzony.")
            else:
                print(f"Indeks '{index_name}' już istnieje.")
            
            return True
        except ElasticsearchException as e:
            print(f"Błąd Elasticsearch: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Nie można utworzyć indeksu: {str(e)}"
            )
    
    def index_document(self, index_name, document_id, document):
        """Indeksowanie dokumentu w Elasticsearch"""
        try:
            self.es.index(
                index=index_name,
                id=document_id,
                body=document
            )
            # Odświeżenie indeksu, aby zmiany były widoczne natychmiast
            self.es.indices.refresh(index=index_name)
            return True
        except ElasticsearchException as e:
            print(f"Błąd Elasticsearch: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Nie można zindeksować dokumentu: {str(e)}"
            )
    
    def search(self, index_name, query, size=10):
        """Wyszukiwanie w Elasticsearch"""
        try:
            search_query = {
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": ["content^3", "title^2", "filename", "court_name"],
                        "fuzziness": "AUTO"
                    }
                },
                "highlight": {
                    "fields": {
                        "content": {},
                        "title": {}
                    },
                    "pre_tags": ["<strong>"],
                    "post_tags": ["</strong>"]
                },
                "size": size
            }
            
            response = self.es.search(
                index=index_name,
                body=search_query
            )
            
            results = []
            for hit in response["hits"]["hits"]:
                result = {
                    "id": hit["_id"],
                    "score": hit["_score"],
                    "source": hit["_source"],
                    "highlights": hit.get("highlight", {})
                }
                results.append(result)
            
            return results
        except ElasticsearchException as e:
            print(f"Błąd Elasticsearch: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Nie można wykonać wyszukiwania: {str(e)}"
            )
    
    def delete_document(self, index_name, document_id):
        """Usuwanie dokumentu z Elasticsearch"""
        try:
            self.es.delete(
                index=index_name,
                id=document_id
            )
            # Odświeżenie indeksu, aby zmiany były widoczne natychmiast
            self.es.indices.refresh(index=index_name)
            return True
        except ElasticsearchException as e:
            print(f"Błąd Elasticsearch: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Nie można usunąć dokumentu: {str(e)}"
            )
    
    def delete_index(self, index_name):
        """Usuwanie indeksu z Elasticsearch"""
        try:
            if self.es.indices.exists(index=index_name):
                self.es.indices.delete(index=index_name)
                print(f"Indeks '{index_name}' usunięty.")
            return True
        except ElasticsearchException as e:
            print(f"Błąd Elasticsearch: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Nie można usunąć indeksu: {str(e)}"
            )
