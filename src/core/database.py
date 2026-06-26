from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from src.core.config import get_settings

settings = get_settings()

# Engine assíncrona usando asyncpg
engine = create_async_engine(settings.DATABASE_URL, echo=False)

# Fábrica de sessões (transações) para o banco
AsyncSessionLocal = sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

Base = declarative_base()

async def get_db():
    """
    Dependency Injection para o FastAPI.
    Garante que cada requisição HTTP abra e feche a conexão com o banco com segurança.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()