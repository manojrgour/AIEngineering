import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_list_faqs():
    response = client.get("/faqs")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert "title" in data[0]