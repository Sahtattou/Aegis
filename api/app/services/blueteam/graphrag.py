from pydantic import BaseModel, Field


class GraphRagResult(BaseModel):
    evidence: list[str] = Field(default_factory=list)


def retrieve_context(query: str) -> GraphRagResult:
    _ = query
    return GraphRagResult([
            "Similar attack pattern seen in prior incident #A-102",
            "Node relation: Campaign->CredentialHarvesting",
        ]
    )
