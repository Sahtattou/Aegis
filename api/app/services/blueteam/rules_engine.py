from pydantic import BaseModel,Field

class RulesResult(BaseModel):
    matched: bool
    matched_rules: list[str] = Field(default_factory=list)
    decision: str | None = None
    confidence: float | None = None




def apply_rules(text: str) -> RulesResult:
    lowered = text.lower()
    if "urgent transfer" in lowered or "verify password" in lowered:
        return RulesResult(
            matched=True,
            matched_rules=["phishing_keywords_v1"],
            decision="malicious",
            confidence=0.95,
        )
    return RulesResult(matched=False)

