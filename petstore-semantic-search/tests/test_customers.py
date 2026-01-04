import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_get_customer():
    response = client.get("/customers/1")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "John"