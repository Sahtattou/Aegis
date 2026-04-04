from pydantic import BaseModel


class Attack(BaseModel):
    id: str
    content: str
    source: str = "redteam"


class Detection(BaseModel):
    attack_id: str
    label: str


class BlindSpot(BaseModel):
    attack_id: str
    reason: str
