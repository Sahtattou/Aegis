
import json
import re
from pathlib import Path
from typing import Literal
from pydantic import BaseModel, Field


Decision = Literal["malicious", "suspicious", "benign"]
MatcherType = Literal["substring", "regex"]

class RuleDefinition(BaseModel):
    id: str
    name: str
    pattern: str
    matcher: MatcherType = "substring"
    decision: Decision = "suspicious"
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)
    enabled: bool = True

class RulesResult(BaseModel):
    matched: bool
    matched_rules: list[str] = Field(default_factory=list)
    decision: Decision | None = None
    confidence: float | None = None
    evidence: list[str] = Field(default_factory=list)


def _default_rules_path() -> Path:
    # api/app/services/blueteam/rules_engine.py -> api/data/kb/tunisian_signatures.json
    return Path(__file__).resolve().parents[3] / "data" / "kb" / "tunisian_signatures.json"



def load_rules(path: Path | None = None) -> list[RuleDefinition]:
    rules_path = path or _default_rules_path()
    if not rules_path.exists():
        return []
    raw = rules_path.read_text(encoding="utf-8").strip()
    if not raw:
        return []
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid rules JSON at {rules_path}") from exc
    if not isinstance(data, list):
        raise RuntimeError(f"Rules file must be a JSON array: {rules_path}")
    rules = [RuleDefinition.model_validate(item) for item in data]
    return [rule for rule in rules if rule.enabled]



def _rule_matches(text: str, rule: RuleDefinition) -> bool:
    if rule.matcher == "substring":
        return rule.pattern.lower() in text
    return re.search(rule.pattern, text, flags=re.IGNORECASE) is not None



def apply_rules(text: str, rules: list[RuleDefinition]) -> RulesResult:
    matched_rules: list[RuleDefinition] = []
    evidence: list[str] = []
    for rule in rules:
        if _rule_matches(text, rule):
            matched_rules.append(rule)
            evidence.append(f"rule:{rule.id}:{rule.name}")
    if not matched_rules:
        return RulesResult(matched=False)
    best = max(matched_rules, key=lambda rule: rule.confidence)
    return RulesResult(
        matched=True,
        matched_rules=[rule.id for rule in matched_rules],
        decision=best.decision,
        confidence=best.confidence,
        evidence=evidence,
    )