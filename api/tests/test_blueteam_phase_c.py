from app.models.detection import DetectionBand
from app.services.blueteam.llm_evaluator import evaluate_with_llm
from app.services.blueteam.pipeline import (
    _fuse_confidence,
    _resolve_band,
    _resolve_gap_severity,
)


def test_fuse_confidence_weighted_formula() -> None:
    fused = _fuse_confidence(0.8, 0.5)
    assert abs(fused - ((0.6 * 0.8) + (0.4 * 0.5))) < 1e-9


def test_band_thresholds_and_gap_mapping() -> None:
    assert _resolve_band(0.65) == DetectionBand.DETECTED
    assert _resolve_band(0.64) == DetectionBand.UNCERTAIN
    assert _resolve_band(0.40) == DetectionBand.UNCERTAIN
    assert _resolve_band(0.39) == DetectionBand.BLIND_SPOT

    assert _resolve_gap_severity(DetectionBand.DETECTED) == "LOW"
    assert _resolve_gap_severity(DetectionBand.UNCERTAIN) == "MEDIUM"
    assert _resolve_gap_severity(DetectionBand.BLIND_SPOT) == "HIGH"


def test_llm_evaluator_returns_structured_result() -> None:
    result = evaluate_with_llm(
        attack_text="urgent verify password now",
        ioc_summary={
            "url_count": 1,
            "suspicious_domain_count": 1,
            "suspicious_extension_count": 0,
        },
        retrieved_context=["incident:A-102"],
    )
    assert 0.0 <= result.llm_confidence <= 1.0
    assert result.threat_class in {"benign", "suspicious", "malicious"}
    assert isinstance(result.key_indicators, list)
    assert isinstance(result.provenance, str)
    assert result.provenance != ""


def test_phase_d_rule_provenance_and_machine_explanation_present() -> None:
    from fastapi.testclient import TestClient

    from app.service_apps.blueteam import app

    client = TestClient(app)
    payload = {
        "attack_id": "A-phase-d-1",
        "content": "Please verify password now",
        "source": "email",
        "metadata": {},
    }
    response = client.post("/evaluate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["rule_matched"] is True
    assert data["attack_id"] == payload["attack_id"]
    assert data["audit_event_id"].startswith("audit-")
    assert data["rule_rationale"] is not None
    assert data["rule_approved_by"] is not None
    assert isinstance(data["xai_top_contributors"], list)
    assert isinstance(data["explanation_machine"], dict)
