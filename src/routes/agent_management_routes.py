from fastapi import APIRouter
from src.schemas.agent import AgentOptimizeRequest, AgentOptimizeResponse
from src.services.optimizer_service import PromptOptimizerService

router = APIRouter(prefix="/v1/agents", tags=["Gerenciamento de Agentes (Backoffice)"])

@router.post("/optimize", response_model=AgentOptimizeResponse)
async def optimize_agent_prompt(payload: AgentOptimizeRequest):
    """
    Recebe um rascunho de comportamento e devolve um System Prompt otimizado para salvar no banco.
    """
    service = PromptOptimizerService()
    optimized = await service.optimize_draft(payload.draft_behavior)
    
    return AgentOptimizeResponse(optimized_prompt=optimized)