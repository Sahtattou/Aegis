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
    assert data["pipeline_version"] == "1.3.0"
    assert "evaluated_at" in data
    assert "ml_confidence" in data
    assert "class_probability_map" in data
    assert "llm_confidence" in data
    assert "llm_threat_class" in data
    assert "llm_key_indicators" in data
    assert "llm_provenance" in data
    assert "fused_confidence" in data
    assert "detected" in data
    assert "band" in data
    assert "threat_class" in data
    assert "rule_matched" in data
    assert "rule_rationale" in data
    assert "rule_approved_by" in data
    assert "signal_features_count" in data
    assert "ioc_summary" in data
    assert "hand_crafted_features" in data
    assert "payload_hash" in data
    assert "audit_event_id" in data
    assert "pipeline_trace" in data
    assert "xai_top_contributors" in data
    assert "explanation_machine" in data


def test_forensic_timeline_endpoint_shape() -> None:
    evaluate_payload = {
        "attack_id": "A-forensic-1",
        "content": "Please verify password urgently",
        "source": "email",
        "metadata": {},
    }
    evaluate_response = client.post("/evaluate", json=evaluate_payload)
    assert evaluate_response.status_code == 200

    response = client.get(f"/forensics/{evaluate_payload['attack_id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["schema_version"] == "forensic.timeline.v1"
    assert data["attack_id"] == evaluate_payload["attack_id"]
    assert "events" in data
    assert isinstance(data["events"], list)
    assert "total_events" in data
    assert "data_completeness" in data


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
    assert data["rule_rationale"] is not None
    assert data["rule_approved_by"] is not None
    assert data["signal_features_count"] >= 10
    assert data["ioc_summary"]["url_count"] >= 0
    assert "urgency_count" in data["hand_crafted_features"]
    assert data["llm_provenance"] in {
        "llm_fallback_heuristic",
        "openai_error_fallback",
        "rule_prefilter_short_circuit",
    } or data["llm_provenance"].startswith("openai:")
    assert data["class_probability_map"] != {}
    assert (
        abs(
            data["fused_confidence"]
            - ((0.6 * data["ml_confidence"]) + (0.4 * data["llm_confidence"]))
        )
        < 1e-9
    )
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
    assert (
        abs(
            data["fused_confidence"]
            - ((0.6 * data["ml_confidence"]) + (0.4 * data["llm_confidence"]))
        )
        < 1e-9
    )
    assert data["llm_provenance"] in {
        "llm_fallback_heuristic",
        "openai_error_fallback",
    } or data["llm_provenance"].startswith("openai:")
    assert isinstance(data["class_probability_map"], dict)
    assert isinstance(data["llm_key_indicators"], list)
    assert isinstance(data["xai_top_contributors"], list)
    assert isinstance(data["explanation_machine"], dict)
    assert "embeddings" in data["pipeline_trace"]
    assert "ioc_extraction" in data["pipeline_trace"]
    assert "feature_builder" in data["pipeline_trace"]
    assert "feature_vector_assembly" in data["pipeline_trace"]
    assert "classifier" in data["pipeline_trace"]
    assert "llm_evaluator" in data["pipeline_trace"]
    assert "xai_shap" in data["pipeline_trace"]
