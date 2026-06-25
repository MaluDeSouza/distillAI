from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_health_check_returns_200():
    """Garante que a API está viva e respondendo no endpoint de health."""
    response = client.get("/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "online"
    assert "project" in data
    assert "version" in data