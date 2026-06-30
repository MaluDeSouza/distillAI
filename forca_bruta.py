import asyncio
from sqlalchemy import text
# Ajuste os imports abaixo se os caminhos estiverem diferentes no seu projeto
from src.core.database import engine, Base
from src.models.agents import AgentModel, KnowledgeBaseModel

async def init_db():
    print("Iniciando injeção forçada no banco...")
    async with engine.begin() as conn:
        # 1. Força a criação da extensão do PgVector primeiro (crucial!)
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        print("Extensão PgVector ativada com sucesso.")
        
        # 2. Manda o SQLAlchemy criar todas as tabelas mapeadas
        await conn.run_sync(Base.metadata.create_all)
        print("Tabelas criadas com sucesso! Pode rodar o FastAPI.")

if __name__ == "__main__":
    asyncio.run(init_db())