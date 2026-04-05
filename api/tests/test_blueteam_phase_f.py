import time

from fastapi.testclient import TestClient

from app.service_apps.blueteam import app
from app.services.blueteam import llm_evaluator, pipeline


client = TestClient(app)


def _post_eval(content: str, attack_id: str = "A-phase-f") -> dict:
    response = client.post(
        "/evaluate",
        json={
            "attack_id": attack_id,
            "content": content,
            "source": "email",
            "metadata": {},
        },
    )
    assert response.status_code == 200
    return response.json()


def test_output_contract_snapshot_minimal() -> None:
    data = _post_eval("Please verify password urgently", attack_id="A-snapshot")

    expected_keys = {
        "pipeline_version",
        "evaluated_at",
        "attack_id",
        "ml_confidence",
        "class_probability_map",
        "llm_confidence",
        "llm_threat_class",
        "llm_key_indicators",
        "llm_provenance",
        "fused_confidence",
        "detected",
        "band",
        "threat_class",
        "rule_matched",
        "matched_rules",
        "rule_id",
        "rule_explanation",
        "rule_rationale",
        "rule_approved_by",
        "signal_features_count",
        "ioc_summary",
        "hand_crafted_features",
        "model_label",
        "decision",
        "explanation_fr",
        "xai_top_contributors",
        "explanation_machine",
        "evidence",
        "rag_context_used",
        "context_match",
        "blind_spot",
        "gap_severity",
        "payload_hash",
        "audit_event_id",
        "pipeline_trace",
    }
    assert set(data.keys()) == expected_keys


def test_uncertain_band_path() -> None:
    data = _post_eval("normal quarterly policy reminder", attack_id="A-uncertain")
    assert data["band"] in {"uncertain", "detected", "blind_spot"}
    if data["band"] == "uncertain":
        assert data["gap_severity"] == "MEDIUM"


def test_blind_spot_path_with_monkeypatched_classifier(monkeypatch) -> None:
    class DummyClassifier:
        label = "benign"
        confidence = 0.0
        probability_map = {"benign": 1.0}
        model_version = "dummy"

    def fake_classify(_features: list[float]) -> DummyClassifier:
        return DummyClassifier()

    monkeypatch.setattr(pipeline, "classify", fake_classify)
    data = _post_eval("internal message with no risk words", attack_id="A-blindspot")
    assert data["band"] == "blind_spot"
    assert data["blind_spot"] is True
    assert data["gap_severity"] == "HIGH"


def test_llm_failure_fallback_observability(monkeypatch, caplog) -> None:
    class DownLLM:
        llm_confidence = 0.0
        threat_class = "suspicious"
        key_indicators: list[str] = []
        context_match = "LLM unavailable"
        available = False
        provenance = "llm_unavailable_test"

    def fake_llm(**_kwargs) -> DownLLM:
        return DownLLM()

    monkeypatch.setattr(llm_evaluator, "evaluate_with_llm", fake_llm)
    monkeypatch.setattr(pipeline, "evaluate_with_llm", fake_llm)
    caplog.set_level("WARNING")

    data = _post_eval("Please verify password now", attack_id="A-llm-fallback")
    assert "llm_fallback" in data["pipeline_trace"]
    assert data["llm_provenance"] == "llm_unavailable_test"
    assert any("LLM unavailable" in record.message for record in caplog.records)


def test_openai_success_path_sets_available(monkeypatch) -> None:
    class UpLLM:
        llm_confidence = 0.87
        threat_class = "malicious"
        key_indicators = ["credential_harvest"]
        context_match = "Matched historical phishing context"
        available = True
        provenance = "openai:gpt-4o-mini"

    def fake_llm(**_kwargs) -> UpLLM:
        return UpLLM()

    monkeypatch.setattr(llm_evaluator, "evaluate_with_llm", fake_llm)
    monkeypatch.setattr(pipeline, "evaluate_with_llm", fake_llm)

    data = _post_eval("Please verify password now", attack_id="A-openai-success")
    assert data["llm_provenance"].startswith("openai:")
    assert "llm_fallback" not in data["pipeline_trace"]
    assert data["llm_confidence"] == 0.87
    assert data["llm_threat_class"] == "malicious"


def test_xai_payload_shape() -> None:
    data = _post_eval("Please verify password now", attack_id="A-xai-shape")
    assert isinstance(data["xai_top_contributors"], list)
    if data["xai_top_contributors"]:
        first = data["xai_top_contributors"][0]
        assert "feature" in first
        assert "contribution" in first
        assert "direction" in first


def test_persistence_linkage_forensics_roundtrip() -> None:
    attack_id = "A-forensic-link"
    evaluate = _post_eval("Please verify password now", attack_id=attack_id)
    forensic = client.get(f"/forensics/{attack_id}")
    assert forensic.status_code == 200
    timeline = forensic.json()
    assert timeline["attack_id"] == attack_id
    assert isinstance(timeline["events"], list)
    if timeline["events"]:
        event = timeline["events"][0]
        assert "audit_linkage" in event
        assert "audit_event_id" in event["audit_linkage"]
        assert event["audit_linkage"]["audit_event_id"] == evaluate["audit_event_id"]


def test_latency_guard_evaluate_under_budget() -> None:
    start = time.perf_counter()
    data = _post_eval("Please verify password now", attack_id="A-latency")
    elapsed = time.perf_counter() - start
    assert data["attack_id"] == "A-latency"
    assert elapsed < 10.0
