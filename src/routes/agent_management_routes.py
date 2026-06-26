from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status,Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from typing import Annotated


from src.core.database import get_db
from src.services.batch_service import BatchIngestionService
from src.schemas.agent import AgentOptimizeRequest, AgentOptimizeResponse
from src.services.optimizer_service import PromptOptimizerService
from src.models.agents import AgentModel

router = APIRouter(prefix="/v1/agents", tags=["Gerenciamento de Agentes (Backoffice)"])

@router.post("/optimize", response_model=AgentOptimizeResponse)
async def optimize_agent_prompt(payload: AgentOptimizeRequest):
    """
    Recebe um rascunho de comportamento e devolve um System Prompt otimizado para salvar no banco.
    """
    service = PromptOptimizerService()
    optimized = await service.optimize_draft(payload.draft_behavior)
    
    return AgentOptimizeResponse(optimized_prompt=optimized)

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_agent_with_knowledge(
    # Utilizando Annotated, blindamos o OpenAPI para renderizar o Swagger perfeitamente
    nome: Annotated[str, Form(...)],
    tipo: Annotated[str, Form()] = "Flash",
    comportamento: Annotated[str, Form()] = "",
    status_agente: Annotated[str, Form()] = "draft",
    files: Annotated[List[UploadFile], File(description="Anexe os manuais/históricos em .txt ou .csv")] = [],
    db: AsyncSession = Depends(get_db)
):
    """
    Cria um agente recebendo os dados textuais + Arquivos (multipart/form-data) na mesma requisição.
    """
    # 1. Instancia e salva o Agente principal no banco de dados
    novo_agente = AgentModel(
        nome=nome,
        tipo=tipo,
        comportamento=comportamento,
        status=status_agente
    )
    db.add(novo_agente)
    await db.commit()
    await db.refresh(novo_agente) # Pega o ID gerado pelo banco
    
    agent_id = novo_agente.id
    resultado_conhecimento = None

    # 2. Se o usuário anexou arquivos reais (ignorando envios vazios), processa o lote
    if files and len(files) > 0 and files.filename:
        batch_service = BatchIngestionService(db)
        resultado_conhecimento = await batch_service.process_batch(agent_id, files)

    return {
        "message": "Agente criado com sucesso",
        "agent_id": agent_id,
        "knowledge_processed": resultado_conhecimento
    }
    
@router.post("/teste")
async def teste(file: UploadFile = File(...)):
    return {"ok": True}