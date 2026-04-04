from pydantic import BaseModel, Field


class RedTeamRunRequest(BaseModel):
    target: str = Field(min_length=1)
    objective: str = Field(min_length=1)
    n_attacks: int = Field(default=3, ge=1, le=20)


class RedTeamAttackCandidate(BaseModel):
    persona: str
    attack_id: str
    content: str
    severity: str
    techniques: list[str]
    embedding: list[float]
    novelty_score: float = Field(ge=0.0, le=1.0)
    max_similarity: float = Field(ge=0.0, le=1.0)


class RedTeamRunResponse(BaseModel):
    status: str
    target: str
    objective: str
    n_attacks: int = Field(ge=1)
    attacks: list[RedTeamAttackCandidate]
