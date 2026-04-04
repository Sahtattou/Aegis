from app.services.blueteam.rules_engine import load_rules


def test_rules_loads_non_empty() -> None:
    rules = load_rules()
    assert len(rules) >= 1
