from app.services.redteam.attack_generator import generate_attack


def test_redteam_attack_has_required_fields() -> None:
    attack = generate_attack()
    assert "id" in attack
    assert "content" in attack
    assert "source" in attack
