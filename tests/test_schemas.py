import pytest
from pydantic import ValidationError
from src.schemas.distiller import TroubleshootingStep

def test_troubleshooting_step_validation():
    """Garante que o Pydantic levante erro se a IA não retornar todos os campos obrigatórios."""
    
    # Simulando um retorno perfeito da IA
    valid_data = {
        "sintoma": "Luz piscando",
        "diagnostico": "Cabo solto",
        "solucao_passo_a_passo": ["Verifique o cabo", "Reinicie o roteador"],
        "quando_chamar_humano": "Se o cabo estiver rompido"
    }
    
    step = TroubleshootingStep(**valid_data)
    assert step.sintoma == "Luz piscando"
    
    # Simulando uma alucinação da IA (faltando a lista de passos)
    invalid_data = {
        "sintoma": "Luz piscando",
        "diagnostico": "Cabo solto",
        "quando_chamar_humano": "Sempre"
    }
    
    # O teste passa se o Pydantic barrar a criação e jogar o erro ValidationError
    with pytest.raises(ValidationError):
        TroubleshootingStep(**invalid_data)
        
def test_troubleshooting_step_type_error():
    """Garante que o Pydantic barre tipos errados (ex: string no lugar de lista)."""
    invalid_type_data = {
        "sintoma": "Luz vermelha",
        "diagnostico": "Cabo solto",
        "solucao_passo_a_passo": "Reinicie o roteador", # ERRO: Isso é texto livre, o contrato exige uma lista!
        "quando_chamar_humano": "Se o cabo estiver rompido"
    }
    
    # O teste passa com sucesso se o Pydantic estourar o ValidationError
    with pytest.raises(ValidationError):
        TroubleshootingStep(**invalid_type_data)