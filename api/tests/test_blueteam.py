from fastapi.testclient import TestClient

from app.config import settings
from app.service_apps.blueteam import app

client = TestClient(app)


def test_evaluate_contract_valid():
    payload = {
        "attack_id": "A-1",
        "content": "Please verify password urgently",
        "source": "email",
        "metadata": {"lang": "fr"},
    }
    response = client.post("/evaluate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["attack_id"] == "A-1"
    assert "decision" in data
    assert "confidence" in data
    assert "pipeline_trace" in data


def test_evaluate_contract_missing_field():
    response = client.post("/evaluate", json={"content": "missing id"})
    assert response.status_code == 422


def test_evaluate_rules_path():
    payload = {
        "attack_id": "A-2",
        "content": "Please verify password now",
        "source": "email",
        "metadata": {},
    }
    response = client.post("/evaluate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["matched_rules"] != []
    assert data["decision"] in {"malicious", "suspicious", "benign"}


def test_evaluate_ml_path():
    payload = {
        "attack_id": "A-3",
        "content": "Normal internal notification about policy update",
        "source": "email",
        "metadata": {},
    }
    response = client.post("/evaluate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["matched_rules"] == []
    assert "embeddings" in data["pipeline_trace"]
    assert "classifier" in data["pipeline_trace"]
