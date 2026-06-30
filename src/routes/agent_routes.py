from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload # Essencial para relações 1:N no AsyncSQLAlchemy

from src.core.database import get_db
from src.services.agent_service import SupportAgentFactory
from src.models.agents import AgentModel

router = APIRouter(prefix="/v1/chat", tags=["Runtime do Agente"])

# O schema agora recebe apenas o ID do agente e a mensagem
class ChatRequest(BaseModel):
    agent_id: int = Field(..., description="ID do agente no banco de dados.")
    message: str = Field(..., description="Mensagem atual do usuário no chat.")
    history: List[Dict[str, str]] = Field(default=[], description="Histórico da sessão (opcional nesta versão base).")

class ChatResponse(BaseModel):
    reply: str = Field(..., description="Resposta de texto do Agente de IA.")

@router.post("/interact", response_model=ChatResponse)
async def interact_endpoint(payload: ChatRequest, db: AsyncSession = Depends(get_db)):
    """
    Busca o agente no banco, acopla a base destilada no bot e processa a mensagem.
    """
    # 1. Busca o agente e faz o Eager Loading (traz as regras de conhecimento junto)
    query = select(AgentModel).where(AgentModel.id == payload.agent_id).options(
        selectinload(AgentModel.knowledge_bases)
    )
    result = await db.execute(query)
    agent_db = result.scalar_one_or_none()

    if not agent_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Agente não encontrado no banco de dados."
        )

    # 2. Instancia a fábrica e monta o agente dinâmico com dados do banco
    factory = SupportAgentFactory()
    agent = factory.build_dynamic_agent(agent_db)
    
    # 3. Roda a interação com o modelo Flash
    response = agent.run(payload.message)
    
    return ChatResponse(reply=response.content)