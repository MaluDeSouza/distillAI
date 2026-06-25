from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Fonte única de verdade para as configurações do DistillAI.
    O Pydantic valida automaticamente os tipos e levanta erro se algo faltar no .env.
    """
    PROJECT_NAME: str = "DistillAI"
    DATABASE_URL: str
    GEMINI_API_KEY: str
    ENV: str = "dev"

    # Configuração estrita do Pydantic v2 para buscar as variáveis do arquivo .env
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra="ignore"
    )

@lru_cache
def get_settings() -> Settings:
    """
    Retorna a instância de configurações em cache.
    Evita leituras repetidas em disco e previne variáveis globais soltas no módulo.
    """
    return Settings()