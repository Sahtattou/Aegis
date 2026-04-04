from typing import Literal
from pydantic import BaseModel , Field

DecisionLabel = Literal["malicious","suspicious","benign"]

class EvaluateRequest(BaseModel):
    attack_id: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)
    source: str | None = None
    metadata: dict[str, str] = Field(default_factory=dict)
class EvaluateResponse(BaseModel):
    attack_id: str
    decision: DecisionLabel
    confidence: float = Field(..., ge=0.0, le=1.0)
    matched_rules: list[str] = Field(default_factory=list)
    model_label: str | None = None
    explanation_fr: str
    evidence: list[str] = Field(default_factory=list)
    pipeline_trace: list[str] = Field(default_factory=list)