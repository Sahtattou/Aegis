from uuid import uuid4


def generate_attack() -> dict[str, str]:
    attack_id = f"atk-{uuid4()}"
    content = "Urgent account verification request targeting employee credentials"
    return {
        "id": attack_id,
        "content": content,
        "source": "redteam",
    }
