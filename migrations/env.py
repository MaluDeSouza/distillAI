import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

# 1. Nossos imports mágicos
import pgvector.sqlalchemy # ESSENCIAL: Ensina o Alembic a ler a coluna Vector
from src.core.config import get_settings
from src.core.database import Base
# IMPORTANTE: Você PRECISA importar os modelos aqui para o Alembic "enxergá-los"
from src.models.agents import AgentModel, KnowledgeBaseModel 

settings = get_settings()

config = context.config

# 2. Injeta a URL do banco direto do nosso .env, ignorando o que tá no alembic.ini
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 3. Aponta para os metadados dos nossos modelos
target_metadata = Base.metadata
print(f"🔥 TABELAS RECONHECIDAS: {Base.metadata.tables.keys()}")
print(f"🔌 BANCO ALVO: {settings.DATABASE_URL}")