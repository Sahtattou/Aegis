from pydantic import BaseModel


class Rule(BaseModel):
    id: str
    pattern: str


class ProposedRule(BaseModel):
    pattern: str
    justification: str
