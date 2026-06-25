from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.1.0",
    description="Engine de IA para destilação de logs de suporte e geração de RAG",
)

# Configuração de CORS padrão
# (Em produção, o wildcard "*" deve ser trocado pelo domínio real do front-end)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["System"])
async def health_check() -> dict[str, str]:
    """
    Endpoint de verificação de integridade da API.
    Utilizado por Load Balancers e painéis de monitoramento para saber se o sistema está vivo.
    """
    return {
        "status": "online",
        "project": settings.PROJECT_NAME,
        "environment": settings.ENV,
        "version": app.version
    }