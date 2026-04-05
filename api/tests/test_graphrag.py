from app.services.blueteam.graphrag import retrieve_context


def test_graphrag_returns_evidence() -> None:
    result = retrieve_context("sample")
    assert len(result.evidence) >= 1
    assert isinstance(result.context_ids, list)
    assert isinstance(result.context_match, str)
