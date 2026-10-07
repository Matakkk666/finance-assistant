from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_health_check():
    """Тест проверяет, что сервер запускается и отвечает."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "API is running"}
