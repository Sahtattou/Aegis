from app.db.repository import Repository


def test_create_blue_evaluation_graceful_without_driver() -> None:
    repo = Repository(None)
    result = repo.create_blue_evaluation(
        detection_id="det-1",
        attack_id="A-1",
        content="payload",
        source="email",
        pipeline_version="1.3.0",
        ml_confidence=0.9,
        llm_confidence=0.5,
        fused_confidence=0.74,
        decision="malicious",
        threat_class="malicious",
        detected=True,
        band="detected",
        blind_spot=False,
        gap_severity="LOW",
        payload_hash="sha256:abc",
        context_ids=[],
        audit_event_id="audit-1",
    )
    assert result == {}


def test_get_attack_forensic_timeline_graceful_without_driver() -> None:
    repo = Repository(None)
    timeline = repo.get_attack_forensic_timeline("A-1")
    assert timeline["attack_id"] == "A-1"
    assert timeline["events"] == []
    assert timeline["total_events"] == 0
    assert timeline["data_completeness"] == "degraded"
