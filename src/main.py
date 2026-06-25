from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.core.config import get_settings

# Importando as nossas novas rotas
from src.routes.distiller_routes import router as distiller_router
from src.routes.agent_routes import router as agent_router

settings = get_settings()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.1.0",
    description="Engine de IA para destilação de logs de suporte e geração de RAG",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Acoplando as rotas ao servidor principal
app.include_router(distiller_router)
app.include_router(agent_router)

@app.get("/health", tags=["System"])
async def health_check() -> dict[str, str]:
    return {
        "status": "online",
        "project": settings.PROJECT_NAME,
        "environment": settings.ENV,
        "version": app.version
    }