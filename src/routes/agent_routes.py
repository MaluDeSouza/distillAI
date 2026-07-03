from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import re

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
    chunks: List[str] = Field(default=[], description="Trechos do RAG utilizados como contexto.")

@router.post("/interact", response_model=ChatResponse)
async def interact_endpoint(payload: ChatRequest, db: AsyncSession = Depends(get_db)):
    """
    Busca o agente no banco, acopla a base destilada no bot e processa a mensagem.
    """
    # 1. Busca o agente e faz o Eager Loading
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
    
    mensagem_final = payload.message

    if payload.history:
        # Monta um bloco de texto estruturado com a conversa
        bloco_historico = "--- INÍCIO DO HISTÓRICO DA SESSÃO ---\n"
        for msg in payload.history:
            papel = "Cliente" if msg["role"] == "user" else "Suporte (Você)"
            bloco_historico += f"{papel}: {msg['content']}\n"
        bloco_historico += "--- FIM DO HISTÓRICO ---\n\n"
        
        # Anexa a nova dúvida ao final do contexto
        mensagem_final = f"{bloco_historico}Nova mensagem do Cliente: {payload.message}"
    
    # 3. Roda a interação passando o pacote completo UMA ÚNICA VEZ
    response = agent.run(mensagem_final)
    
    # Limpa as tags no formato da resposta
    texto_limpo = re.sub(r'\]+\]', '', response.content)
    
    # 4. Extração dos Chunks para exibição
    recuperados = []
    try:
        if agent.knowledge:
            # Mantemos payload.message aqui para o RAG não ler o histórico
            relevant_docs = agent.knowledge.search(payload.message)
            recuperados = [doc.content for doc in relevant_docs] if relevant_docs else []
    except Exception as e:
        print(f"Aviso: Falha ao extrair chunks. Erro: {e}")
    
    return ChatResponse(
        reply=texto_limpo.strip(), 
        chunks=recuperados
    )