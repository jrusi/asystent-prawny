from minio import Minio
from minio.error import S3Error
from io import BytesIO
import os
from fastapi import HTTPException, status

class MinioClient:
    def __init__(self, endpoint, access_key, secret_key):
        """Inicjalizacja klienta MinIO"""
        self.client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=False  # W środowisku produkcyjnym powinno być True
        )
        self.bucket_name = "legal-assistant"

    def check_connection(self):
        """Sprawdzenie połączenia i inicjalizacja bucketa"""
        try:
            # Sprawdzenie czy bucket istnieje
            if not self.client.bucket_exists(self.bucket_name):
                # Utworzenie bucketa
                self.client.make_bucket(self.bucket_name)
                print(f"Bucket '{self.bucket_name}' utworzony.")
            else:
                print(f"Bucket '{self.bucket_name}' już istnieje.")
            return True
        except S3Error as e:
            print(f"Błąd MinIO: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Nie można połączyć się z MinIO: {str(e)}"
            )

    def create_user_bucket(self, user_id):
        """Tworzenie struktury katalogów dla użytkownika"""
        try:
            # W MinIO nie ma katalogów, ale możemy symulować je za pomocą prefiksów
            # Tworzymy pusty plik jako marker
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=f"{user_id}/.keep",
                data=BytesIO(b""),
                length=0
            )
            return True
        except S3Error as e:
            print(f"Błąd MinIO: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Nie można utworzyć struktury katalogów: {str(e)}"
            )

    def create_case_directory(self, case_path):
        """Tworzenie struktury katalogów dla sprawy"""
        try:
            # Tworzymy pusty plik jako marker
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=f"{case_path}/.keep",
                data=BytesIO(b""),
                length=0
            )
            return True
        except S3Error as e:
            print(f"Błąd MinIO: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Nie można utworzyć struktury katalogów: {str(e)}"
            )

    def upload_file(self, file_path, content):
        """Wgrywanie pliku do MinIO"""
        try:
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=file_path,
                data=BytesIO(content),
                length=len(content)
            )
            return True
        except S3Error as e:
            print(f"Błąd MinIO: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Nie można wgrać pliku: {str(e)}"
            )

    def download_file(self, file_path):
        """Pobieranie pliku z MinIO"""
        try:
            response = self.client.get_object(
                bucket_name=self.bucket_name,
                object_name=file_path
            )
            content = response.read()
            response.close()
            response.release_conn()
            return content
        except S3Error as e:
            print(f"Błąd MinIO: {e}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Nie można pobrać pliku: {str(e)}"
            )

    def delete_file(self, file_path):
        """Usuwanie pliku z MinIO"""
        try:
            self.client.remove_object(
                bucket_name=self.bucket_name,
                object_name=file_path
            )
            return True
        except S3Error as e:
            print(f"Błąd MinIO: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Nie można usunąć pliku: {str(e)}"
            )

    def list_files(self, prefix):
        """Listowanie plików z określonym prefiksem"""
        try:
            objects = self.client.list_objects(
                bucket_name=self.bucket_name,
                prefix=prefix,
                recursive=True
            )
            return [obj.object_name for obj in objects]
        except S3Error as e:
            print(f"Błąd MinIO: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Nie można wylistować plików: {str(e)}"
            )
