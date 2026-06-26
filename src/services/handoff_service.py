from google import genai
from google.genai import types
from typing import List, Dict
from src.core.config import get_settings
from src.schemas.distiller import KnowledgeBaseTemplate
from src.schemas.handoff import HandoffPayload

settings = get_settings()

class HandoffService:
    def __init__(self):
        """Inicializa o serviço de transbordo utilizando a SDK moderna."""
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
        self.system_instruction = (
            "Você é um supervisor de triagem técnica de suporte de TI de Nível 2.\n"
            "Sua missão é analisar o histórico de uma conversa frustrada entre um bot de IA e um usuário final.\n"
            "Cruze as mensagens com as regras operacionais fornecidas para identificar o sintoma original, "
            "listar o que o robô tentou resolver, diagnosticar a causa exata da falha operacional "
            "e mapear a postura emocional do cliente.\n"
            "Preencha rigorosamente todos os campos do schema JSON solicitado, sem inventar dados fora do histórico."
        )

    async def generate_human_handoff_payload(
        self, chat_history: List[Dict[str, str]], config: KnowledgeBaseTemplate
    ) -> HandoffPayload:
        """
        Processa o histórico e gera o payload tipado para consumo do atendente humano.
        """
        # Compila a lista de dicionários do chat em texto legível para a LLM
        history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in chat_history])
        
        prompt = (
            f"=== REGRAS OPERACIONAIS DO BOT ===\n"
            f"Categoria: {config.categoria}\n\n"
            f"=== HISTÓRICO DE MENSAGENS DO CHAT ===\n"
            f"{history_text}"
        )

        # Configuração de Structured Outputs com o novo payload Pydantic
        generation_config = types.GenerateContentConfig(
            system_instruction=self.system_instruction,
            response_mime_type="application/json",
            response_schema=HandoffPayload,
            temperature=0.1  # Baixa temperatura para evitar inferências fantasiosas
        )

        response = await self.client.aio.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=generation_config
        )

        return HandoffPayload.model_validate_json(response.text)