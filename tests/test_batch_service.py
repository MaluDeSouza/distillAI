import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import UploadFile
from src.services.batch_service import BatchIngestionService

@pytest.mark.asyncio
@patch("src.services.batch_service.KnowledgeDistillerService.distill_logs")
async def test_batch_ingestion_service_success(mock_distill, tmp_path):
    # 1. Simular uma resposta da IA
    mock_response = MagicMock()
    mock_kb = MagicMock()
    mock_kb.categoria = "Rede"
    mock_kb.model_dump.return_value = {"procedimentos": [{"sintoma": "luz vermelha"}]}
    mock_response.knowledge_bases = [mock_kb]
    
    # Configuramos o mock para retornar essa simulação assincronamente
    mock_distill.return_value = mock_response

    # 2. Criar arquivos simulados
    file_mock = AsyncMock(spec=UploadFile)
    file_mock.read.return_value = b"Cliente: Minha internet caiu."

    # 3. Mockar a sessão do Banco de Dados
    db_session_mock = AsyncMock()

    # 4. Executar o serviço
    service = BatchIngestionService(db_session=db_session_mock)
    result = await service.process_batch(agent_id=1, files=[file_mock, file_mock])

    # 5. Validações (Asserts)
    assert result["arquivos_processados"] == 2
    assert result["regras_salvas_com_sucesso"] == 2
    assert result["falhas_de_extracao"] == 0
    
    # Garante que tentamos adicionar no banco de dados e que o commit foi chamado
    assert db_session_mock.add.call_count == 2
    db_session_mock.commit.assert_awaited_once()