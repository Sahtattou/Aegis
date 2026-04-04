import pytest


@pytest.fixture
def sample_payload() -> dict[str, str]:
    return {"text": "sample"}
