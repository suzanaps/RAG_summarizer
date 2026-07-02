import os
from functools import lru_cache
from pathlib import Path
from dotenv import find_dotenv
from pydantic import Field, SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from enum import Enum

# Define a raiz do projeto (subindo 2 níveis a partir de app/core/)
BASE_DIR = Path(__file__).resolve().parents[2]


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

    
    # Secrets e LLM
    OPENAI_API_KEY: SecretStr | None = None
    GOOGLE_API_KEY: SecretStr | None = None

    MODEL_NAME: str = os.environ.get("SUMMARY_MODEL_NAME", "gemini-2.5-flash-lite")

    # --- Limites de upload/processamento ---
    # Tamanho máximo por arquivo (bytes). Padrão: 20 MB.
    MAX_FILE_SIZE_BYTES: int = int(os.environ.get("MAX_FILE_SIZE_BYTES", 20 * 1024 * 1024))
    # Número máximo de páginas por PDF.
    MAX_PAGES_PER_PDF: int = int(os.environ.get("MAX_PAGES_PER_PDF", 200))
    # Número máximo de caracteres extraídos por PDF (proteção extra além de páginas).
    MAX_CHARS_PER_PDF: int = int(os.environ.get("MAX_CHARS_PER_PDF", 600_000))
    # Número máximo de arquivos por requisição em lote.
    MAX_FILES_PER_REQUEST: int = int(os.environ.get("MAX_FILES_PER_REQUEST", 10))

    # --- Parâmetros de chunking/agrupamento ---
    CHUNK_SIZE: int = int(os.environ.get("CHUNK_SIZE", 1000))
    CHUNK_OVERLAP: int = int(os.environ.get("CHUNK_OVERLAP", 200))
    CHUNKS_PER_GROUP: int = int(os.environ.get("CHUNKS_PER_GROUP", 5))

    # --- Concorrência ---
    # Limita quantas chamadas simultâneas ao modelo são feitas ao resumir grupos de chunks.
    MAX_CONCURRENT_LLM_CALLS: int = int(os.environ.get("MAX_CONCURRENT_LLM_CALLS", 3))




@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

# Instância global para ser importada em outros arquivos
settings = get_settings()