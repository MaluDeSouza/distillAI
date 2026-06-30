from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, Any
from pydantic import BaseModel, ValidationError

from src.core.database import get_db
from src.services.batch_service import BatchIngestionService
from src.schemas.agent import AgentOptimizeRequest, AgentOptimizeResponse
from src.services.optimizer_service import PromptOptimizerService
from src.models.agents import AgentModel

router = APIRouter(prefix="/v1/agents", tags=["Gerenciamento de Agentes (Backoffice)"])

# --- AQUI ESTÁ A MAGIA PARA ENGANAR O SWAGGER ---
# Sobrescrevemos o comportamento do schema do Pydantic para forçar o botão de upload
class SwaggerUploadFile(UploadFile):
    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema: Any, handler: Any) -> dict[str, Any]:
        return {"type": "string", "format": "binary"}

class AgentCreatePayload(BaseModel):
    nome: str
    tipo: str = "Flash"
    comportamento: str = ""
    status_agente: str = "draft"

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_agent_with_knowledge(
    payload: Annotated[str, Form(description="JSON string contendo metadados (nome, tipo, etc)")],
    # Usamos a nossa classe customizada aqui!
    files: Annotated[list[SwaggerUploadFile], File(description="Anexe os manuais em .txt")],
    db: AsyncSession = Depends(get_db)
):
    """
    Cria um agente recebendo um JSON estrito + múltiplos arquivos na mesma requisição.
    """
    try:
        dados_agente = AgentCreatePayload.model_validate_json(payload)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
            detail=f"Erro de formatação no JSON do payload: {e.errors()}"
        )

    novo_agente = AgentModel(
        nome=dados_agente.nome,
        tipo=dados_agente.tipo,
        comportamento=dados_agente.comportamento,
        status=dados_agente.status_agente
    )
    
    db.add(novo_agente)
    await db.commit()
    await db.refresh(novo_agente)
    
    resultado_conhecimento = None

    # Validamos usando a lista normal de arquivos
    if files and len(files) > 0 and files[0].filename:
        batch_service = BatchIngestionService(db)
        resultado_conhecimento = await batch_service.process_batch(novo_agente.id, files)

    return {
        "message": "Agente criado com sucesso",
        "agent_id": novo_agente.id,
        "knowledge_processed": resultado_conhecimento
    }