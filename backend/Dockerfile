FROM python:3.9-slim

# Ustaw zmienne środowiskowe
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Zainstaluj wymagane pakiety systemowe
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    tesseract-ocr \
    tesseract-ocr-pol \
    poppler-utils \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Utwórz i ustaw katalog roboczy
WORKDIR /app

# Skopiuj plik z wymaganiami
COPY backend/requirements.txt .

# Zainstaluj zależności Pythona
RUN pip install --no-cache-dir -r requirements.txt

# Skopiuj cały kod backendu
COPY backend/ .

# Utwórz katalogi tymczasowe
RUN mkdir -p /tmp

# Uruchom aplikację
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
