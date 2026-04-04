from pydantic import BaseModel


class AuditEntry(BaseModel):
    id: str
    event_type: str
    details: str
