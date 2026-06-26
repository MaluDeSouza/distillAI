from pydantic import BaseModel, Field
from typing import List

class HandoffPayload(BaseModel):
    """Contrato estrito que formata o dossiê enviado para o atendente humano."""
    status: str = Field(default="escalated", description="Status operacional do ticket.")
    sintoma_inicial: str = Field(..., description="O sintoma principal ou queixa descrita pelo cliente no primeiro contato.")
    tentativas_realizadas: List[str] = Field(..., description="Lista ordenada de diagnósticos ou ações que o robô tentou aplicar com o usuário.")
    motivo_escalonamento: str = Field(..., description="A justificativa clara de por que o atendimento automatizado falhou ou parou.")
    comportamento_usuario: str = Field(..., description="Breve resumo do estado emocional ou postura do cliente durante o chat (ex: irritado, cooperativo, confuso).")