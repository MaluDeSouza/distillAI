from agno.agent import Agent
from agno.models.google import Gemini
from src.core.config import get_settings
from src.schemas.distiller import KnowledgeBaseTemplate

settings = get_settings()

class SupportAgentFactory:
    def __init__(self):
        """
        Inicializa a fábrica de agentes. 
        O modelo Flash é mandatório aqui para garantir baixíssima latência (tempo real).
        """
        self.model = Gemini(id="gemini-2.5-flash", api_key=settings.GEMINI_API_KEY)

    def build_dynamic_agent(self, config: KnowledgeBaseTemplate) -> Agent:
        """
        Constrói o agente Agno injetando as regras destiladas dinamicamente nas instruções do sistema.
        """
        # Compilando o JSON em um System Prompt estruturado e restritivo
        regras_str = f"Você é um agente de suporte técnico Nível 1 especializado na categoria: {config.categoria}.\n\n"
        regras_str += "Procedimentos operacionais padronizados:\n"
        
        for proc in config.procedimentos:
            regras_str += f"- Sintoma Relatado: '{proc.sintoma}'\n"
            regras_str += f"  Diagnóstico de Base: {proc.diagnostico}\n"
            regras_str += "  Ações de Resolução (Execute UM DE CADA VEZ e aguarde o retorno do usuário):\n"
            for i, passo in enumerate(proc.solucao_passo_a_passo, 1):
                regras_str += f"    {i}. {passo}\n"
            regras_str += f"  [GATILHO DE HANDOFF]: {proc.quando_chamar_humano}\n\n"

        regras_str += (
            "REGRAS DE ENGAJAMENTO (CRÍTICO):\n"
            "1. Siga estritamente a sequência de passos correspondente ao sintoma do usuário.\n"
            "2. Nunca envie a lista completa de tarefas de uma vez. Peça uma ação e aguarde a resposta.\n"
            "3. Se todas as ações falharem ou o cenário do usuário atingir o [GATILHO DE HANDOFF], "
            "interrompa o troubleshooting imediatamente, avise que está escalonando o caso e encerre a interação técnica."
        )

        # Retorna o agente devidamente engatilhado com o contexto
        return Agent(
            model=self.model,
            description=f"Robô de Atendimento Dinâmico - {config.categoria}",
            instructions=regras_str,
            markdown=True
        )