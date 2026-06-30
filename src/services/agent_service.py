from agno.agent import Agent
from agno.models.google import Gemini
from src.core.config import get_settings
from src.models.agents import AgentModel # Importando nosso modelo do DB

settings = get_settings()

class SupportAgentFactory:
    def __init__(self):
        """
        Inicializa a fábrica de agentes. 
        O modelo Flash é mandatório aqui para garantir baixíssima latência.
        """
        self.model = Gemini(id="gemini-2.5-flash", api_key=settings.GEMINI_API_KEY)

    def build_dynamic_agent(self, agent_db: AgentModel) -> Agent:
        """
        Constrói o agente Agno fundindo o 'comportamento' do banco com as regras JSON destiladas.
        """
        # 1. Puxa a diretriz de comportamento (o System Prompt otimizado na Fase 2)
        regras_str = f"{agent_db.comportamento}\n\n"
        regras_str += "BASE DE CONHECIMENTO (PROCEDIMENTOS OPERACIONAIS):\n"
        
        # 2. Itera pelas bases atreladas ao agente e destrincha o JSON da coluna regras_payload
        for kb in agent_db.knowledge_bases:
            regras_str += f"\n--- CATEGORIA: {kb.categoria.upper()} ---\n"
            
            # O regras_payload é uma lista de dicionários no banco (originada do Pydantic na Fase 3)
            for proc in kb.regras_payload:
                regras_str += f"- Sintoma Relatado: '{proc.get('sintoma', '')}'\n"
                regras_str += f"  Diagnóstico de Base: {proc.get('diagnostico', '')}\n"
                regras_str += "  Ações de Resolução (Execute UM DE CADA VEZ e aguarde o retorno do usuário):\n"
                
                # Monta a lista de passos
                for i, passo in enumerate(proc.get('solucao_passo_a_passo', []), 1):
                    regras_str += f"    {i}. {passo}\n"
                    
                regras_str += f"  [GATILHO DE HANDOFF]: {proc.get('quando_chamar_humano', '')}\n"

        # 3. Adiciona as regras inegociáveis de engajamento
        regras_str += (
            "\nREGRAS DE ENGAJAMENTO (CRÍTICO):\n"
            "1. Siga estritamente a sequência de passos correspondente ao sintoma do usuário.\n"
            "2. Nunca envie a lista completa de tarefas de uma vez. Peça uma ação e aguarde a resposta.\n"
            "3. Se todas as ações falharem ou o cenário do usuário atingir o [GATILHO DE HANDOFF], "
            "interrompa o troubleshooting imediatamente, avise que está escalonando o caso e encerre a interação técnica."
        )

        # 4. Retorna o Agente "Blindado"
        return Agent(
            model=self.model,
            description=f"Robô de Atendimento Dinâmico - {agent_db.nome}",
            instructions=regras_str,
            markdown=True
        )