from google import genai
from google.genai import types
from src.core.config import get_settings
from src.schemas.distiller import DistillerResponse

settings = get_settings()

class KnowledgeDistillerService:
    def __init__(self):
        """
        Inicializa o Client da nova SDK google-genai.
        """
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
        self.system_instruction = (
            "Você é um Engenheiro de Suporte Nível 3 Sênior. "
            "Leia os históricos brutos de suporte, ignore saudações e dados sensíveis. "
            "Extraia EXCLUSIVAMENTE sintomas, diagnósticos, soluções e restrições. "
            "Você DEVE preencher todos os campos exigidos no schema JSON."
        )

    async def distill_logs(self, raw_logs: str) -> DistillerResponse:
        """
        Gera o conteúdo utilizando a API aio (assíncrona) do novo SDK.
        """
        # Configuração de schema usando o novo google.genai.types
        config = types.GenerateContentConfig(
            system_instruction=self.system_instruction,
            response_mime_type="application/json",
            response_schema=DistillerResponse,
            temperature=0.1
        )

        # Chamada assíncrona nova
        response = await self.client.aio.models.generate_content(
            model='gemini-2.5-pro',
            contents=raw_logs,
            config=config
        )

        return DistillerResponse.model_validate_json(response.text)