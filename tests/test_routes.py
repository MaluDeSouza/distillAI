import io
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
from src.main import app

client = TestClient(app)

@patch("src.routes.distiller_routes.KnowledgeDistillerService.distill_logs", new_callable=AsyncMock)
def test_distill_route_success(mock_distill_logs):
    """Garante que a rota de upload e processamento funciona isoladamente."""
    
    # Fingimos a resposta do nosso serviço
    mock_distill_logs.return_value = {
        "knowledge_bases": [
            {
                "categoria": "Rede",
                "procedimentos": [] # Vazio para manter o teste curto e direto
            }
        ]
    }
    
    # Criamos um arquivo falso direto na memória (buffer) para enviar pelo TestClient
    file_content = b"Cliente: oi. Atendente: ola."
    files = {"file": ("dummy_chat.txt", io.BytesIO(file_content), "text/plain")}
    
    response = client.post("/v1/distill", files=files)
    
    assert response.status_code == 200
    data = response.json()
    assert "knowledge_bases" in data
    assert mock_distill_logs.called

@patch("src.routes.agent_routes.SupportAgentFactory.build_dynamic_agent")
def test_agent_interact_route(mock_build_agent):
    """Garante que o payload viaja corretamente da rota HTTP para o Agente."""
    
    # Simulamos o retorno do Agno
    mock_response = MagicMock()
    mock_response.content = "Por favor, reinicie seu modem."
    
    mock_agent = MagicMock()
    mock_agent.run.return_value = mock_response
    mock_build_agent.return_value = mock_agent

    payload = {
        "message": "Minha internet caiu",
        "history": [],
        "template": {
            "categoria": "Rede",
            "procedimentos": [
                {
                    "sintoma": "Caiu",
                    "diagnostico": "Cabo solto",
                    "solucao_passo_a_passo": ["Checar cabo"],
                    "quando_chamar_humano": "Se estiver rompido"
                }
            ]
        }
    }

    response = client.post("/v1/chat/interact", json=payload)
    
    assert response.status_code == 200
    assert response.json() == {"reply": "Por favor, reinicie seu modem."}
    assert mock_build_agent.called