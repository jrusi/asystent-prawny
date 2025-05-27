import os
from typing import List

class Settings:
    PROJECT_NAME: str = "Asystent Prawny"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api"
    
    # CORS Settings
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",  # React development server
        "http://localhost",
        "https://localhost",
        "http://localhost:8080",
    ]
    
    # Add any GitHub Codespaces URLs if they exist
    if os.getenv("CODESPACE_NAME"):
        codespace_name = os.getenv("CODESPACE_NAME")
        domain = os.getenv("GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN", "app.github.dev")
        if codespace_name:
            # Add wildcard for all subdomains of the codespace
            BACKEND_CORS_ORIGINS.extend([
                f"https://{codespace_name}-*{domain}",  # Wildcard for all ports
                f"https://*.{domain}"  # Broader wildcard as fallback
            ])
    
    # Database settings
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "asystent_prawny")
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}/{POSTGRES_DB}"
    )
    
    # MinIO settings
    MINIO_ENDPOINT: str = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    MINIO_ROOT_USER: str = os.getenv("MINIO_ROOT_USER", "minioadmin")
    MINIO_ROOT_PASSWORD: str = os.getenv("MINIO_ROOT_PASSWORD", "minioadmin")
    MINIO_SECURE: bool = os.getenv("MINIO_SECURE", "false").lower() == "true"

    def get_cors_origins(self) -> List[str]:
        """Get all CORS origins including any dynamic ones"""
        origins = self.BACKEND_CORS_ORIGINS.copy()
        
        # Add any custom origins from environment variable
        if os.getenv("ADDITIONAL_CORS_ORIGINS"):
            origins.extend(
                origin.strip()
                for origin in os.getenv("ADDITIONAL_CORS_ORIGINS").split(",")
                if origin.strip()
            )
            
        # For development in Codespaces, allow all GitHub dev domains
        if any("app.github.dev" in origin for origin in origins):
            origins.append("https://*.app.github.dev")
        
        return origins

settings = Settings() 