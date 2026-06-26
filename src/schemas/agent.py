from pydantic import BaseModel, Field

class AgentOptimizeRequest(BaseModel):
    draft_behavior: str = Field(..., description="Rascunho simples escrito pelo usuário. Ex: 'um bot educado que resolve internet'")

class AgentOptimizeResponse(BaseModel):
    optimized_prompt: str = Field(..., description="O System Prompt profissional gerado pela nossa IA.")