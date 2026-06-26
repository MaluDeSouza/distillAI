import pytest
from unittest.mock import AsyncMock, patch
from src.services.handoff_service import HandoffService
from src.schemas.handoff import HandoffPayload
from src.schemas.distiller import KnowledgeBaseTemplate, TroubleshootingStep

@pytest.fixture
def sample_context():
    """Gabarito operacional fictício para o teste."""
    step = TroubleshootingStep(
        sintoma="Luz vermelha",
        diagnostico="Cabo solto ou danificado",
        solucao_passo_a_passo=["Verificar cabo PON amarelo", "Desligar da tomada por 1 min"],
        quando_chamar_humano="Se houver rompimento físico da fiação"
    )
    return KnowledgeBaseTemplate(categoria="Fibra Óptica", procedimentos=[step])

@pytest.fixture
def sample_history():
    """Histórico simulando um bot falhando devido a uma restrição física."""
    return [
        {"role": "user", "content": "Oi, minha internet caiu e tá com luz vermelha piscando no modem."},
        {"role": "model", "content": "Olá! Vamos checar o cabo amarelo de fibra atrás do aparelho. Ele está firme?"},
        {"role": "user", "content": "Nossa, acabei de olhar aqui e meu gato mordeu o cabo, tá quebrado no chão."},
        {"role": "model", "content": "Entendi. Como há danos físicos no cabo, vou encaminhar você para o suporte técnico humano."}
    ]

# --- TESTE UNITÁRIO (COM MOCK) ---
@pytest.mark.asyncio
@patch("src.services.handoff_service.genai.Client")
async def test_generate_handoff_with_mock(mock_client_class, sample_context, sample_history):
    fake_json = """
    {
        "status": "escalated",
        "sintoma_inicial": "Luz vermelha piscando no modem",
        "tentativas_realizadas": ["Verificação do cabo PON amarelo"],
        "motivo_escalonamento": "Cabo quebrado fisicamente pelo animal de estimação",
        "comportamento_usuario": "Cooperativo"
    }
    """
    mock_client_instance = AsyncMock()
    mock_client_class.return_value = mock_client_instance
    
    mock_response = AsyncMock()
    mock_response.text = fake_json
    mock_client_instance.aio.models.generate_content = AsyncMock(return_value=mock_response)

    service = HandoffService()
    result = await service.generate_human_handoff_payload(sample_history, sample_context)

    assert isinstance(result, HandoffPayload)
    assert result.status == "escalated"
    assert "quebrado" in result.motivo_escalonamento
    mock_client_instance.aio.models.generate_content.assert_called_once()

# --- TESTE DE INTEGRAÇÃO (REAL) ---
@pytest.mark.asyncio
@pytest.mark.integration
async def test_generate_handoff_real_integration(sample_context, sample_history):
    service = HandoffService()
    result = await service.generate_human_handoff_payload(sample_history, sample_context)

    assert isinstance(result, HandoffPayload)
    assert result.status == "escalated"
    assert len(result.sintoma_inicial) > 0
    assert len(result.tentativas_realizadas) > 0
    # Valida se a inteligência do Flash pescou o comportamento ou a causa raiz do gato
    assert any(x in result.motivo_escalonamento.lower() for x in ["gato", "quebrado", "mordeu", "físico", "dano"])