import pytest
from unittest.mock import patch, MagicMock
from agno.agent import Agent
from src.schemas.distiller import KnowledgeBaseTemplate, TroubleshootingStep
from src.services.agent_service import SupportAgentFactory

@pytest.fixture
def dummy_template():
    """Fixture do Pytest com dados falsos controlados para testarmos a injeção."""
    step = TroubleshootingStep(
        sintoma="Internet lenta",
        diagnostico="Gargalo no DNS",
        solucao_passo_a_passo=["Limpar cache", "Reiniciar Roteador"],
        quando_chamar_humano="Se a lentidão persistir após 2 reinicializações"
    )
    return KnowledgeBaseTemplate(
        categoria="Rede",
        procedimentos=[step]
    )

def test_agent_instantiation(dummy_template):
    """Critério 1: Garante que a fábrica devolve uma instância válida do Agno Agent."""
    factory = SupportAgentFactory()
    agent = factory.build_dynamic_agent(dummy_template)
    
    assert isinstance(agent, Agent)
    assert agent.model.id == "gemini-2.5-flash"

def test_context_injection(dummy_template):
    """Critério 2: Garante que as strings vitais foram parar no 'cérebro' do robô."""
    factory = SupportAgentFactory()
    agent = factory.build_dynamic_agent(dummy_template)
    
    # As instruções injetadas ficam armazenadas no atributo instructions
    instrucoes = agent.instructions
    
    # Validando se as regras cruciais foram convertidas em texto para a LLM
    assert "Reiniciar Roteador" in instrucoes
    assert "Gargalo no DNS" in instrucoes
    assert "Se a lentidão persistir após 2 reinicializações" in instrucoes
    assert "Rede" in instrucoes

@patch("agno.agent.Agent.run")
def test_simulated_interaction(mock_run, dummy_template):
    """Critério 3: Garante que o robô roda o ciclo de chat sem explodir a aplicação."""
    # Configurando o mock para fingir que a IA respondeu
    mock_response = MagicMock()
    mock_response.content = "Olá! Vamos limpar o cache primeiro. Me avise quando fizer."
    mock_run.return_value = mock_response

    factory = SupportAgentFactory()
    agent = factory.build_dynamic_agent(dummy_template)
    
    # Simulamos o usuário chamando o robô
    resposta = agent.run("Minha internet está muito lenta")
    
    # Verificamos se o método de resposta do Agno foi chamado corretamente
    assert mock_run.called
    assert resposta.content == "Olá! Vamos limpar o cache primeiro. Me avise quando fizer."