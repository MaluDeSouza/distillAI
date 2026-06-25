from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List, Dict
from src.schemas.distiller import KnowledgeBaseTemplate
from src.services.agent_service import SupportAgentFactory

router = APIRouter(prefix="/v1/chat", tags=["Runtime do Agente"])

# Schemas específicos para a requisição de Chat
class ChatRequest(BaseModel):
    message: str = Field(..., description="Mensagem atual do usuário no chat.")
    history: List[Dict[str, str]] = Field(default=[], description="Histórico da sessão (opcional nesta versão base).")
    template: KnowledgeBaseTemplate = Field(..., description="O JSON com as regras de negócio injetadas.")

class ChatResponse(BaseModel):
    reply: str = Field(..., description="Resposta de texto do Agente de IA.")

@router.post("/interact", response_model=ChatResponse)
async def interact_endpoint(payload: ChatRequest):
    """
    Injeta o template dinâmico no bot em tempo real e processa a mensagem do usuário.
    """
    factory = SupportAgentFactory()
    agent = factory.build_dynamic_agent(payload.template)
    
    # Roda a interação com o modelo Flash
    response = agent.run(payload.message)
    
    return ChatResponse(reply=response.content)