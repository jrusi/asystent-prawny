import os
import time
from sqlalchemy import create_engine
from minio import Minio
from minio.error import S3Error
from elasticsearch import Elasticsearch
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Konfiguracja z zmiennych środowiskowych
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/legal_assistant")
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
ELASTIC_URL = os.getenv("ELASTIC_URL", "http://elasticsearch:9200")

def init_db():
    logger.info("Inicjalizacja połączenia z bazą danych...")
    for attempt in range(10):
        try:
            engine = create_engine(DATABASE_URL)
            conn = engine.connect()
            conn.close()
            logger.info("Połączenie z bazą danych ustanowione.")
            return True
        except Exception as e:
            logger.warning(f"Próba {attempt+1}/10: Nie można połączyć się z bazą danych: {e}")
            time.sleep(5)
    
    logger.error("Nie udało się połączyć z bazą danych po 10 próbach.")
    return False

def init_minio():
    logger.info("Inicjalizacja MinIO...")
    for attempt in range(10):
        try:
            client = Minio(
                MINIO_ENDPOINT,
                access_key=MINIO_ACCESS_KEY,
                secret_key=MINIO_SECRET_KEY,
                secure=False
            )
            
            # Utworzenie bucketa dla aplikacji
            bucket_name = "legal-assistant"
            if not client.bucket_exists(bucket_name):
                client.make_bucket(bucket_name)
                logger.info(f"Bucket '{bucket_name}' utworzony.")
            else:
                logger.info(f"Bucket '{bucket_name}' już istnieje.")
            
            return True
        except S3Error as e:
            logger.warning(f"Próba {attempt+1}/10: Nie można połączyć się z MinIO: {e}")
            time.sleep(5)
    
    logger.error("Nie udało się połączyć z MinIO po 10 próbach.")
    return False

def init_elasticsearch():
    logger.info("Inicjalizacja Elasticsearch...")
    for attempt in range(10):
        try:
            es = Elasticsearch([ELASTIC_URL])
            if es.ping():
                logger.info("Połączenie z Elasticsearch ustanowione.")
                return True
            else:
                logger.warning(f"Próba {attempt+1}/10: Elasticsearch nie odpowiada.")
        except Exception as e:
            logger.warning(f"Próba {attempt+1}/10: Nie można połączyć się z Elasticsearch: {e}")
        
        time.sleep(5)
    
    logger.error("Nie udało się połączyć z Elasticsearch po 10 próbach.")
    return False

if __name__ == "__main__":
    logger.info("Rozpoczynam inicjalizację usług...")
    
    db_ok = init_db()
    minio_ok = init_minio()
    es_ok = init_elasticsearch()
    
    if db_ok and minio_ok and es_ok:
        logger.info("Wszystkie usługi zostały zainicjalizowane pomyślnie.")
    else:
        logger.error("Nie wszystkie usługi zostały zainicjalizowane.")
        exit(1)
