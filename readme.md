# Asystent Prawny - System do analizy spraw prawnych

Asystent Prawny to kompleksowa aplikacja webowa do zarządzania i analizy dokumentów prawnych. Platforma umożliwia użytkownikom przetwarzanie dokumentów sprawy, automatyczne pobieranie aktów prawnych z ISAP oraz podobnych orzeczeń z SAOS, a następnie zadawanie pytań dotyczących sprawy.

## Kluczowe funkcjonalności

- **Zarządzanie sprawami** - tworzenie i organizacja spraw prawnych
- **Zarządzanie dokumentami** - dodawanie i przechowywanie dokumentów związanych ze sprawą
- **Integracja z ISAP** - wyszukiwanie i pobieranie aktów prawnych związanych ze sprawą
- **Integracja z SAOS** - wyszukiwanie i pobieranie orzeczeń sądowych podobnych do sprawy
- **System pytań i odpowiedzi** - zadawanie pytań o sprawę i otrzymywanie odpowiedzi opartych na dodanych dokumentach, aktach prawnych i orzeczeniach
- **Bezpieczne przechowywanie danych** - izolacja danych różnych spraw i użytkowników
- **Intuicyjny interfejs użytkownika** - prosty i przejrzysty interfejs

## Architektura systemu

Aplikacja została zbudowana w architekturze mikroserwisowej, z wykorzystaniem kontenerów Docker:

- **Frontend** - interfejs użytkownika zbudowany w React i Material UI
- **Backend API** - serwer FastAPI obsługujący zapytania i logikę biznesową
- **Baza danych** - PostgreSQL do przechowywania metadanych
- **System plików** - MinIO do przechowywania dokumentów
- **Silnik wyszukiwania** - Elasticsearch do indeksowania i wyszukiwania w dokumentach
- **Silnik RAG** - do generowania odpowiedzi na pytania użytkownika

## Wymagania

- Docker i Docker Compose
- Minimum 4GB RAM
- 10GB wolnego miejsca na dysku
- Dostęp do internetu (dla integracji z ISAP i SAOS)

## Uruchomienie aplikacji

1. Sklonuj repozytorium:
   ```
   git clone https://github.com/twoja-organizacja/asystent-prawny.git
   cd asystent-prawny
   ```

2. Skonfiguruj zmienne środowiskowe (stwórz plik `.env` w głównym katalogu projektu):
   ```
   DATABASE_URL=postgresql://postgres:postgres@db:5432/legal_assistant
   MINIO_ROOT_USER=minioadmin
   MINIO_ROOT_PASSWORD=minioadmin
   JWT_SECRET=twoj_tajny_klucz
   OPENAI_API_KEY=twoj_klucz_api_openai
   ```

3. Uruchom aplikację za pomocą Docker Compose:
   ```
   docker-compose up -d   
   ```

4. Aplikacja będzie dostępna pod adresem: http://localhost:3000

## Pierwsze kroki po uruchomieniu

1. Zarejestruj nowe konto
2. Zaloguj się do aplikacji
3. Utwórz nową sprawę
4. Dodaj dokumenty do sprawy
5. Wyszukaj odpowiednie akty prawne i orzeczenia
6. Zadaj pytania dotyczące sprawy

## Bezpieczeństwo i prywatność danych

Aplikacja została zaprojektowana z myślą o zapewnieniu bezpieczeństwa i prywatności danych:

- Każda sprawa jest izolowana, a dane są przechowywane w izolowanych przestrzeniach
- Wszystkie połączenia są zabezpieczone
- Autentykacja oparta na tokenach JWT
- Regularna walidacja danych wejściowych
- Dane każdej sprawy pozostają tylko w obrębie tej sprawy

## Rozwijanie aplikacji

### Struktura projektu

```
asystent-prawny/
├── backend/                 # Kod serwera FastAPI
│   ├── auth.py              # Moduł autentykacji
│   ├── database.py          # Konfiguracja bazy danych
│   ├── elasticsearch_client.py # Klient Elasticsearch
│   ├── isap_client.py       # Klient ISAP
│   ├── main.py              # Główny plik aplikacji
│   ├── models.py            # Modele danych
│   ├── rag_engine.py        # Silnik RAG
│   ├── saos_client.py       # Klient SAOS
│   ├── schemas.py           # Schematy Pydantic
│   └── storage.py           # Obsługa przechowywania plików
├── frontend/                # Aplikacja React
│   ├── public/              # Pliki statyczne
│   └── src/                 # Kod źródłowy
│       ├── contexts/        # Konteksty React
│       ├── layouts/         # Komponenty układu
│       └── pages/           # Strony aplikacji
├── docker-compose.yml       # Konfiguracja Docker Compose
└── README.md                # Dokumentacja projektu
```

### Rozbudowa funkcjonalności

Możliwe kierunki rozbudowy aplikacji:

1. Dodanie systemu komentarzy i adnotacji do dokumentów
2. Implementacja zaawansowanego OCR dla skanowanych dokumentów
3. Rozszerzenie integracji o inne źródła danych prawnych
4. Dodanie funkcji eksportu sprawy do PDF/DOCX
5. Implementacja zaawansowanej analizy statystycznej orzeczeń

## Licencja

Ta aplikacja jest dostępna na licencji [MIT](LICENSE).

## Autor

Imię Nazwisko - [Kontakt](mailto:email@example.com)
