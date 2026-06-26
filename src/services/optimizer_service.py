from google import genai
from google.genai import types
from src.core.config import get_settings

settings = get_settings()

class PromptOptimizerService:
    def __init__(self):
        """Inicializa a IA focada em Engenharia de Prompt."""
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
        self.system_instruction = (
            "Você é um Engenheiro de Prompt Sênior especialista em arquitetar agentes de IA de suporte técnico. "
            "Sua missão é transformar rascunhos informais de usuários em 'System Prompts' profissionais, "
            "claros, impositivos e estruturados. "
            "O prompt gerado deve: \n"
            "1. Definir a persona e o tom de voz.\n"
            "2. Estabelecer regras estritas contra alucinações ou desvios de escopo.\n"
            "3. Ser escrito na primeira pessoa do imperativo para o bot (ex: 'Você é um assistente... Aja assim...').\n"
            "Retorne APENAS o prompt final otimizado. Não adicione saudações, aspas ou explicações."
        )

    async def optimize_draft(self, draft: str) -> str:
        """Recebe o rascunho e devolve a instrução de sistema lapidada."""
        config = types.GenerateContentConfig(
            system_instruction=self.system_instruction,
            temperature=0.7 # Um pouco mais de criatividade aqui é bem-vindo para redigir textos
        )
        
        response = await self.client.aio.models.generate_content(
            model='gemini-2.5-pro',
            contents=draft,
            config=config
        )
        
        return response.text.strip()