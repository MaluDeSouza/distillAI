import pytest
from unittest.mock import AsyncMock, patch
from src.services.distiller_service import KnowledgeDistillerService
from src.schemas.distiller import DistillerResponse

# --- 1. TESTE UNITÁRIO (COM MOCK - NÃO GASTA TOKENS) ---
@pytest.mark.asyncio
@patch("src.services.distiller_service.genai.Client")
async def test_distill_logs_with_mock(mock_client_class):
    """Teste unitário atualizado para a nova SDK google-genai."""
    fake_json_response = """
    {
      "knowledge_bases": [
        {
          "categoria": "Roteador",
          "procedimentos": [
            {
              "sintoma": "Luz vermelha piscando",
              "diagnostico": "Falta de conexão com provedor",
              "solucao_passo_a_passo": ["Verifique o cabo PON", "Reinicie o roteador"],
              "quando_chamar_humano": "Se o cabo PON estiver partido"
            }
          ]
        }
      ]
    }
    """
    
    # Configura o mock para a nova estrutura: client.aio.models.generate_content
    mock_client_instance = AsyncMock()
    mock_client_class.return_value = mock_client_instance
    
    mock_response = AsyncMock()
    mock_response.text = fake_json_response
    mock_client_instance.aio.models.generate_content = AsyncMock(return_value=mock_response)

    service = KnowledgeDistillerService()
    result = await service.distill_logs("Log irrelevante porque o mock intercepta antes.")

    assert isinstance(result, DistillerResponse)
    assert result.knowledge_bases[0].categoria == "Roteador"

# --- 2. TESTE DE INTEGRAÇÃO (BATE NA API REAL DO GEMINI) ---
@pytest.mark.asyncio
@pytest.mark.integration 
async def test_distill_logs_real_integration():
    """
    Bate de verdade na API do Gemini. 
    Marcado com @pytest.mark.integration para podermos ignorar no dia a dia se quisermos.
    """
    log_real = (
        "Cliente: Minha internet caiu e tá com luz vermelha no roteador da intelbras.\n"
        "Atendente: Olá! Tudo bem? Reiniciou o roteador e conferiu o cabo amarelo?\n"
        "Cliente: Sim, tirei da tomada por 1 minuto e não voltou. O cabo tá firme.\n"
        "Atendente: Certo, como o reset não funcionou e o cabo está ok, vou abrir um chamado técnico físico."
    )

    service = KnowledgeDistillerService()
    result = await service.distill_logs(log_real)

    # Validamos se a IA conseguiu extrair a essência da conversa
    assert isinstance(result, DistillerResponse)
    assert len(result.knowledge_bases) > 0
    
    procedimento = result.knowledge_bases[0].procedimentos[0]
    
    assert "luz vermelha" in procedimento.sintoma.lower()
    assert len(procedimento.solucao_passo_a_passo) > 0
    
    # O Gemini extrai a semântica do gatilho, não a palavra exata.
    # Testamos se ele gerou uma instrução real (string com mais de 10 caracteres)
    # e se capturou a essência do problema físico ou persistência do erro.
    condicao = procedimento.quando_chamar_humano.lower()
    
    assert len(condicao) > 10
    assert any(palavra in condicao for palavra in ["persistir", "física", "técnico", "cabo", "reinicialização"])