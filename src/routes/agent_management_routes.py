from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, Any, List
from pydantic import BaseModel, ValidationError

from src.core.database import get_db
from src.services.batch_service import BatchIngestionService
from src.services.optimizer_service import PromptOptimizerService
from src.schemas.agent import AgentOptimizeRequest, AgentOptimizeResponse
from src.models.agents import AgentModel

router = APIRouter(prefix="/v1/agents", tags=["Gerenciamento de Agentes"])

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
    
@router.post("/optimize", response_model=AgentOptimizeResponse)
async def optimize_prompt(request: AgentOptimizeRequest):
    """
    Transforma um rascunho informal em um System Prompt estruturado.
    """
    optimizer = PromptOptimizerService()
    optimized_behavior = await optimizer.optimize_draft(request.draft_behavior)
    return {"optimized_prompt": optimized_behavior}

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_agent_with_knowledge(
    nome: str = Form(..., description="Nome do Agente"),
    tipo: str = Form("Flash", description="Tipo/Modelo do agente"),
    comportamento: str = Form(..., description="Rascunho da persona/comportamento"),
    status_agente: str = Form("draft", description="Status inicial (ex: draft, production)"),
    files: List[SwaggerUploadFile] = File(..., description="Base de conhecimento (.txt)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Criação de agente com campos separados. 
    O comportamento recebido já é a versão final escolhida no front-end.
    """
    # 1. Persistência no banco usando o comportamento exato que veio na requisição
    novo_agente = AgentModel(
        nome=nome,
        tipo=tipo,
        comportamento=comportamento, 
        status=status_agente
    )
    
    db.add(novo_agente)
    await db.commit()
    await db.refresh(novo_agente)    

    # 2. Processamento de conhecimento em batch
    resultado_conhecimento = None
    if files and len(files) > 0 and files[0].filename:
        batch_service = BatchIngestionService(db)
        resultado_bruto = await batch_service.process_batch(novo_agente.id, files)
                
        chunks_extraidos = resultado_bruto if isinstance(resultado_bruto, int) else 0
                
        if isinstance(resultado_bruto, dict):
            chunks_extraidos = resultado_bruto.get("regras_salvas_com_sucesso", 0) 
        else:
            chunks_extraidos = 0
        resultado_conhecimento = {
            "chunks_saved": chunks_extraidos
        }

    return {
        "message": "Agente criado com sucesso.",
        "agent_id": novo_agente.id,
        "optimized_prompt": comportamento,
        "knowledge_processed": resultado_conhecimento 
    }