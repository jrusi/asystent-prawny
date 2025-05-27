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
            secure=False  # Dla lokalnego rozwoju, w produkcji powinno być True
        )
        self.bucket_name = "asystent-prawny"
        self.ensure_bucket_exists()

    def ensure_bucket_exists(self):
        """Sprawdzenie czy bucket istnieje, jeśli nie - utworzenie go"""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                print(f"Utworzono bucket: {self.bucket_name}")
            else:
                print(f"Bucket {self.bucket_name} już istnieje")
        except S3Error as e:
            print(f"Błąd MinIO: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Nie można utworzyć bucketa: {str(e)}"
            )

    def check_connection(self):
        """Sprawdzenie połączenia z MinIO"""
        try:
            self.client.bucket_exists(self.bucket_name)
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
            # Tworzymy pusty plik jako marker
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=f"users/{user_id}/.keep",
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

    def delete_case_directory(self, case_path):
        """Usunięcie wszystkich plików sprawy"""
        try:
            # Pobierz listę wszystkich obiektów w katalogu sprawy
            objects = self.client.list_objects(
                bucket_name=self.bucket_name,
                prefix=case_path
            )
            
            # Usuń każdy obiekt
            for obj in objects:
                self.client.remove_object(
                    bucket_name=self.bucket_name,
                    object_name=obj.object_name
                )
            return True
        except S3Error as e:
            print(f"Błąd MinIO: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Nie można usunąć plików sprawy: {str(e)}"
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

    def list_files(self, directory_path):
        """Listowanie plików w katalogu"""
        try:
            objects = self.client.list_objects(
                bucket_name=self.bucket_name,
                prefix=directory_path,
                recursive=True
            )
            return [obj.object_name for obj in objects]
        except S3Error as e:
            print(f"Błąd MinIO: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Nie można pobrać listy plików: {str(e)}"
            )
