from pydantic import BaseModel


class Analyst(BaseModel):
    id: str
    name: str
