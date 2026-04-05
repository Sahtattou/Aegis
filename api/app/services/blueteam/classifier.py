import importlib

from pydantic import BaseModel, Field


class ClassifierResult(BaseModel):
    label: str
    confidence: float = Field(ge=0.0, le=1.0)
    probability_map: dict[str, float] = Field(default_factory=dict)
    model_version: str = "unknown"


def classify(features: list[float]) -> ClassifierResult:
    module = importlib.import_module("app.services.blueteam.model_loader")
    predict_from_features = getattr(module, "predict_from_features")
    prediction = predict_from_features(features)
    return ClassifierResult(
        label=prediction.label,
        confidence=prediction.confidence,
        probability_map=prediction.probability_map,
        model_version=prediction.model_version,
    )
