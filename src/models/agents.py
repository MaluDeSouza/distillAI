from sqlalchemy import Column, String, Integer, ForeignKey, JSON, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from src.core.database import Base

class AgentModel(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    tipo = Column(String(50), default="Flash") # Ex: Flash (mais rápido) ou Pro
    status = Column(String(50), default="draft") # draft ou production
    comportamento = Column(Text, nullable=False) # O System Prompt otimizado
    criado_em = Column(DateTime(timezone=True), server_default=func.now())

    # Relacionamento (1:N): Um agente possui várias bases de conhecimento
    knowledge_bases = relationship("KnowledgeBaseModel", back_populates="agent", cascade="all, delete-orphan")

class KnowledgeBaseModel(Base):
    __tablename__ = "knowledge_bases"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    categoria = Column(String(100), nullable=False)
    
    # O pulo do gato: A base de regras não é um texto corrido, é o JSON do Pydantic!
    regras_payload = Column(JSON, nullable=False) 
    
    # O terreno preparado para o RAG futuro (768 dimensões exatas do Gemini Embedder)
    sintoma_embedding = Column(Vector(768), nullable=True) 
    criado_em = Column(DateTime(timezone=True), server_default=func.now())

    agent = relationship("AgentModel", back_populates="knowledge_bases")