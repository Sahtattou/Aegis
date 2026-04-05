from app.services.blueteam.classifier import classify


def test_classifier_fallback_returns_valid_range() -> None:
    result = classify([0.0] * 384)
    assert result.label in {"benign", "suspicious", "malicious"}
    assert 0.0 <= result.confidence <= 1.0
    assert isinstance(result.probability_map, dict)
    assert result.probability_map != {}
    assert abs(sum(result.probability_map.values()) - 1.0) < 1e-6
    assert isinstance(result.model_version, str)
    assert isinstance(result.probability_map, dict)
    assert result.model_version != ""


def test_classifier_probability_map_is_normalized() -> None:
    result = classify([0.0] * 384)
    if result.probability_map:
        total = sum(result.probability_map.values())
        assert 0.99 <= total <= 1.01
