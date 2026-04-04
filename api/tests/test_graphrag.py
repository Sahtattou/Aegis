from app.services.blueteam.graphrag import retrieve_context


def test_graphrag_returns_evidence() -> None:
    result = retrieve_context("sample")
    assert len(result.evidence) >= 1
