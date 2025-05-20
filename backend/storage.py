import io
import os
import logging
import tempfile
from typing import Optional, List, Dict, Any, Union
from minio import Minio
from minio.error import S3Error
from PyPDF2 import PdfReader
import docx2txt
import pytesseract
from PIL import Image
import fitz  # PyMuPDF

logger = logging.getLogger(__name__)

class StorageManager:
    """
    Klasa do zarządzania przechowywaniem plików w MinIO
    """
    
    def __init__(
        self,
        minio_endpoint: str = "minio:9000",
        minio_access_key: str = "minioadmin",
        minio_secret_key: str = "minioadmin",
        minio_secure: bool = False,
        bucket_name: str = "legal-assistant"
    ):
        """
        Inicjalizacja menedżera przechowywania.
        
        Args:
            minio_endpoint: Adres serwera MinIO
            minio_access_key: Klucz dostępu do MinIO
            minio_secret_key: Tajny klucz dostępu do MinIO
            minio_secure: Czy używać HTTPS
            bucket_name: Nazwa bucketu
        """
        self.minio_client = Minio(
            minio_endpoint,
            access_key=minio_access_key,
            secret_key=minio_secret_key,
            secure=minio_secure
        )
        self.bucket_name = bucket_name
        
        # Utworzenie bucketu, jeśli nie istnieje
        try:
            if not self.minio_client.bucket_exists(self.bucket_name):
                self.minio_client.make_bucket(self.bucket_name)
                logger.info(f"Utworzono bucket {self.bucket_name}")
        except S3Error as e:
            logger.error(f"Błąd podczas tworzenia bucketu: {e}")
    
    async def upload_file(self, file_path: str, file_content: bytes) -> bool:
        """
        Przesyła plik do MinIO.
        
        Args:
            file_path: Ścieżka pliku w bucket
            file_content: Zawartość pliku w bajtach
            
        Returns:
            True jeśli operacja się powiodła, False w przeciwnym razie
        """
        try:
            content_stream = io.BytesIO(file_content)
            content_size = len(file_content)
            content_type = self._get_content_type(file_path)
            
            self.minio_client.put_object(
                self.bucket_name,
                file_path,
                content_stream,
                content_size,
                content_type=content_type
            )
            
            logger.info(f"Plik {file_path} został przesłany do MinIO")
            return True
            
        except S3Error as e:
            logger.error(f"Błąd podczas przesyłania pliku: {e}")
            return False
    
    async def get_file(self, file_path: str) -> Optional[bytes]:
        """
        Pobiera plik z MinIO.
        
        Args:
            file_path: Ścieżka pliku w bucket
            
        Returns:
            Zawartość pliku w bajtach lub None jeśli wystąpił błąd
        """
        try:
            response = self.minio_client.get_object(
                self.bucket_name,
                file_path
            )
            
            content = response.read()
            response.close()
            response.release_conn()
            
            return content
            
        except S3Error as e:
            logger.error(f"Błąd podczas pobierania pliku: {e}")
            return None
    
    async def delete_file(self, file_path: str) -> bool:
        """
        Usuwa plik z MinIO.
        
        Args:
            file_path: Ścieżka pliku w bucket
            
        Returns:
            True jeśli operacja się powiodła, False w przeciwnym razie
        """
        try:
            self.minio_client.remove_object(
                self.bucket_name,
                file_path
            )
            
            logger.info(f"Plik {file_path} został usunięty z MinIO")
            return True
            
        except S3Error as e:
            logger.error(f"Błąd podczas usuwania pliku: {e}")
            return False
    
    async def extract_text(self, file_path: str, file_type: Optional[str] = None) -> str:
        """
        Ekstrahuje tekst z pliku.
        
        Args:
            file_path: Ścieżka pliku w bucket
            file_type: Typ pliku (np. application/pdf, application/msword)
            
        Returns:
            Wyekstrahowany tekst lub pusty ciąg znaków jeśli wystąpił błąd
        """
        try:
            content = await self.get_file(file_path)
            if not content:
                return ""
            
            # Jeśli nie podano typu pliku, próbujemy go odgadnąć
            if not file_type:
                file_type = self._get_content_type(file_path)
            
            # Ekstrakcja tekstu w zależności od formatu pliku
            if file_type == "application/pdf":
                return self._extract_text_from_pdf(content)
            elif file_type == "application/msword" or file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                return self._extract_text_from_docx(content)
            elif file_type.startswith("image/"):
                return self._extract_text_from_image(content)
            elif file_type == "text/plain":
                return content.decode("utf-8", errors="replace")
            else:
                # Dla nieznanych formatów zwracamy pusty ciąg znaków
                logger.warning(f"Nieobsługiwany format pliku: {file_type}")
                return ""
                
        except Exception as e:
            logger.error(f"Błąd podczas ekstrakcji tekstu: {e}")
            return ""
    
    def _extract_text_from_pdf(self, content: bytes) -> str:
        """
        Ekstrahuje tekst z pliku PDF.
        
        Args:
            content: Zawartość pliku w bajtach
            
        Returns:
            Wyekstrahowany tekst
        """
        try:
            # Utworzenie tymczasowego pliku
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(content)
                tmp_path = tmp.name
            
            # Ekstrakcja tekstu przy użyciu PyMuPDF (fitz)
            try:
                text = ""
                with fitz.open(tmp_path) as doc:
                    for page in doc:
                        text += page.get_text()
                
                # Jeśli PyMuPDF zwrócił pusty tekst, próbujemy użyć PyPDF2
                if not text.strip():
                    with open(tmp_path, "rb") as f:
                        reader = PdfReader(f)
                        text = ""
                        for page in reader.pages:
                            text += page.extract_text() or ""
            
            finally:
                # Usunięcie tymczasowego pliku
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
            
            return text
            
        except Exception as e:
            logger.error(f"Błąd podczas ekstrakcji tekstu z PDF: {e}")
            return ""
    
    def _extract_text_from_docx(self, content: bytes) -> str:
        """
        Ekstrahuje tekst z pliku DOCX.
        
        Args:
            content: Zawartość pliku w bajtach
            
        Returns:
            Wyekstrahowany tekst
        """
        try:
            # Utworzenie tymczasowego pliku
            with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
                tmp.write(content)
                tmp_path = tmp.name
            
            try:
                text = docx2txt.process(tmp_path)
            finally:
                # Usunięcie tymczasowego pliku
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
            
            return text
            
        except Exception as e:
            logger.error(f"Błąd podczas ekstrakcji tekstu z DOCX: {e}")
            return ""
    
    def _extract_text_from_image(self, content: bytes) -> str:
        """
        Ekstrahuje tekst z obrazu przy użyciu OCR.
        
        Args:
            content: Zawartość pliku w bajtach
            
        Returns:
            Wyekstrahowany tekst
        """
        try:
            # Utworzenie tymczasowego pliku
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                tmp.write(content)
                tmp_path = tmp.name
            
            try:
                # Otwarcie obrazu przy użyciu Pillow
                image = Image.open(tmp_path)
                
                # Ekstrakcja tekstu przy użyciu pytesseract (OCR)
                text = pytesseract.image_to_string(image, lang="pol")
            finally:
                # Usunięcie tymczasowego pliku
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
            
            return text
            
        except Exception as e:
            logger.error(f"Błąd podczas ekstrakcji tekstu z obrazu: {e}")
            return ""
    
    def _get_content_type(self, file_path: str) -> str:
        """
        Zwraca typ MIME pliku na podstawie rozszerzenia.
        
        Args:
            file_path: Ścieżka do pliku
            
        Returns:
            Typ MIME pliku
        """
        extension = os.path.splitext(file_path)[1].lower()
        
        mime_types = {
            ".pdf": "application/pdf",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".doc": "application/msword",
            ".txt": "text/plain",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".bmp": "image/bmp",
            ".tiff": "image/tiff",
            ".tif": "image/tiff"
        }
        
        return mime_types.get(extension, "application/octet-stream")
