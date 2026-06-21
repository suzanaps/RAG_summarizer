import os
from functools import lru_cache
from pathlib import Path
from dotenv import find_dotenv
from pydantic import Field, SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from enum import Enum

# Define a raiz do projeto (subindo 2 níveis a partir de app/core/)
BASE_DIR = Path(__file__).resolve().parents[2]

class DatabaseType(str, Enum):
    SQLITE = "sqlite"
    POSTGRES = "postgres"
    MONGO = "mongo"

class Settings(BaseSettings):
    # Configuração de carregamento do .env na raiz
    model_config = SettingsConfigDict(
        env_file=os.path.join(BASE_DIR, ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Configurações Básicas
    app_name: str = "RAG Summarizer"
    api_prefix: str = "/api"
    environment: str = "local"
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 30
    algorithm: str = "HS256"

    # Database
    database_host: str = ""
    database_port: int = 5433
    database_name: str = ""
    database_user: str = ""
    database_password: str = ""
    database_socket: str = ""
    
    # Secrets e LLM
    OPENAI_API_KEY: SecretStr | None = None
    GOOGLE_API_KEY: SecretStr | None = None

    @computed_field
    @property
    def async_database_url(self) -> str:
        # Prioriza o uso do asyncpg (o padrão recomendado para FastAPI/SQLAlchemy async)
        return "postgresql+asyncpg://{}:{}@{}:{}/{}".format(
            self.database_user,
            self.database_password,
            self.database_host,
            self.database_port,
            self.database_name,
        )

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

# Instância global para ser importada em outros arquivos
settings = get_settings()