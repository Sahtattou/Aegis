import importlib

from pydantic import BaseModel, Field


class ClassifierResult(BaseModel):
    label: str
    confidence: float = Field(ge=0.0, le=1.0)


def classify(features: list[float]) -> ClassifierResult:
    module = importlib.import_module("app.services.blueteam.model_loader")
    predict_from_features = getattr(module, "predict_from_features")
    label, confidence = predict_from_features(features)
    return ClassifierResult(label=label, confidence=confidence)
