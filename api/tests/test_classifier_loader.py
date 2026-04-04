from app.services.blueteam.classifier import classify


def test_classifier_fallback_returns_valid_range() -> None:
    result = classify([0.0] * 384)
    assert result.label in {"benign", "suspicious", "malicious"}
    assert 0.0 <= result.confidence <= 1.0
