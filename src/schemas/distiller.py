from pydantic import BaseModel, Field
from typing import List

class TroubleshootingStep(BaseModel):
    """Modelo granular que representa um único fluxo de resolução de problema."""
    
    sintoma: str = Field(
        ..., 
        description="O que o usuário relata no chat de forma desestruturada (ex: 'Luz vermelha piscando', 'internet caiu')."
    )
    diagnostico: str = Field(
        ..., 
        description="A causa raiz técnica identificada pelo suporte humano durante o atendimento."
    )
    solucao_passo_a_passo: List[str] = Field(
        ..., 
        description="Lista ordenada de instruções claras e diretas que o técnico passou para resolver o problema."
    )
    quando_chamar_humano: str = Field(
        ..., 
        description="Gatilho crítico ou restrição operacional de quando a IA deve parar de tentar e realizar o handoff (ex: 'Equipamento fisicamente quebrado')."
    )

class KnowledgeBaseTemplate(BaseModel):
    """Agrupador lógico de procedimentos por domínio ou equipamento."""
    
    categoria: str = Field(
        ..., 
        description="Categoria macro do problema (ex: 'Roteador Wi-Fi', 'Antena Starlink', 'Acesso ao App')."
    )
    procedimentos: List[TroubleshootingStep] = Field(
        ..., 
        description="Lista de passos de troubleshooting pertencentes a esta categoria."
    )

class DistillerResponse(BaseModel):
    """Container raiz esperado como output final da LLM."""
    
    knowledge_bases: List[KnowledgeBaseTemplate] = Field(
        ..., 
        description="Lista consolidada com todas as bases de conhecimento destiladas dos logs."
    )