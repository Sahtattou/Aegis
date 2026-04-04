from pydantic import BaseModel



class ClassifierResult(BaseModel):
    label: str
    confidence: float


def classify(features: list[float]) -> ClassifierResult:
    _ = features
    return ClassifierResult(label="suspicious", confidence=0.72)
