from fastapi.testclient import TestClient

from app.service_apps.blueteam import app

client = TestClient(app)


def test_evaluate_contract_valid() -> None:
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
    assert data["pipeline_version"] == "1.0.0"
    assert "evaluated_at" in data
    assert "ml_confidence" in data
    assert "llm_confidence" in data
    assert "fused_confidence" in data
    assert "detected" in data
    assert "band" in data
    assert "threat_class" in data
    assert "rule_matched" in data
    assert "signal_features_count" in data
    assert "ioc_summary" in data
    assert "hand_crafted_features" in data
    assert "payload_hash" in data
    assert "audit_event_id" in data
    assert "pipeline_trace" in data


def test_evaluate_contract_missing_field() -> None:
    response = client.post("/evaluate", json={"content": "missing id"})
    assert response.status_code == 422


def test_evaluate_rules_path_sets_rule_fields() -> None:
    payload = {
        "attack_id": "A-2",
        "content": "Please verify password now",
        "source": "email",
        "metadata": {},
    }
    response = client.post("/evaluate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["rule_matched"] is True
    assert data["matched_rules"] != []
    assert data["rule_id"] is not None
    assert data["rule_explanation"] is not None
    assert data["signal_features_count"] >= 10
    assert data["ioc_summary"]["url_count"] >= 0
    assert "urgency_count" in data["hand_crafted_features"]
    assert data["decision"] in {"malicious", "suspicious", "benign"}


def test_evaluate_ml_path_sets_routing_fields() -> None:
    payload = {
        "attack_id": "A-3",
        "content": "Normal internal notification about policy update",
        "source": "email",
        "metadata": {},
    }
    response = client.post("/evaluate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["rule_matched"] is False
    assert data["matched_rules"] == []
    assert data["band"] in {"detected", "uncertain", "blind_spot"}
    assert data["gap_severity"] in {"LOW", "MEDIUM", "HIGH"}
    assert data["blind_spot"] in {True, False}
    assert data["signal_features_count"] > 10
    assert "domain_count" in data["ioc_summary"]
    assert "brand_match_count" in data["hand_crafted_features"]
    assert "embeddings" in data["pipeline_trace"]
    assert "ioc_extraction" in data["pipeline_trace"]
    assert "feature_builder" in data["pipeline_trace"]
    assert "feature_vector_assembly" in data["pipeline_trace"]
    assert "classifier" in data["pipeline_trace"]
