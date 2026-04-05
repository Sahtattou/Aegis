from pydantic import BaseModel, Field

from app.db.repository import Repository


class GraphRagResult(BaseModel):
    evidence: list[str] = Field(default_factory=list)
    context_ids: list[str] = Field(default_factory=list)
    context_match: str = ""


def _keyword_overlap_score(query: str, content: str) -> int:
    query_tokens = {token for token in query.lower().split() if len(token) >= 4}
    if not query_tokens:
        return 0
    content_tokens = set(content.lower().split())
    return len(query_tokens.intersection(content_tokens))


def retrieve_context(query: str) -> GraphRagResult:
    repository = Repository()
    try:
        recent_attacks = repository.list_recent_attacks(limit=25)
    except Exception:
        return GraphRagResult(
            evidence=["Graph retrieval unavailable"],
            context_ids=[],
            context_match="Graph unavailable",
        )

    if not recent_attacks:
        return GraphRagResult(
            evidence=["No historical incidents available in graph store"],
            context_ids=[],
            context_match="No graph context",
        )

    ranked = sorted(
        recent_attacks,
        key=lambda attack: _keyword_overlap_score(
            query, str(attack.get("content", ""))
        ),
        reverse=True,
    )
    top = [
        item
        for item in ranked[:3]
        if _keyword_overlap_score(query, str(item.get("content", ""))) > 0
    ]

    if not top:
        top = ranked[:2]

    evidence: list[str] = []
    context_ids: list[str] = []
    for attack in top:
        attack_id = str(attack.get("id", "unknown"))
        source = str(attack.get("source", "unknown"))
        snippet = str(attack.get("content", ""))[:140]
        context_ids.append(attack_id)
        evidence.append(
            f"Graph context attack={attack_id} source={source} snippet='{snippet}'"
        )

    return GraphRagResult(
        evidence=evidence,
        context_ids=context_ids,
        context_match=(
            "Graph context correlated with prior attacks"
            if context_ids
            else "No graph context"
        ),
    )
