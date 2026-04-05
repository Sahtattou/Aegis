import json
from dataclasses import dataclass
from pathlib import Path
from threading import Lock
from typing import Protocol, cast

import joblib
import numpy as np

from app.config import settings


@dataclass
class LoadedModel:
    version: str
    labels: list[str]
    input_dim: int
    model: object


@dataclass
class PredictionResult:
    label: str
    confidence: float
    probability_map: dict[str, float]
    model_version: str


class ProbaModel(Protocol):
    def predict_proba(self, x: np.ndarray) -> np.ndarray: ...


class PredictModel(Protocol):
    def predict(self, x: np.ndarray) -> np.ndarray: ...


_MODEL_LOCK = Lock()
_LOADED_MODEL: LoadedModel | None = None


def _model_root() -> Path:
    root = Path(settings.classifier_model_root)
    if root.is_absolute():
        return root
    return Path(__file__).resolve().parents[4] / root


def _resolve_version_dir() -> Path:
    root = _model_root()
    root.mkdir(parents=True, exist_ok=True)
    if settings.classifier_active_version != "latest":
        return root / settings.classifier_active_version

    version_dirs = [p for p in root.iterdir() if p.is_dir()]
    if not version_dirs:
        raise FileNotFoundError(f"No classifier versions found in {root}")
    version_dirs.sort(key=lambda p: p.name)
    return version_dirs[-1]


def _load_metadata(version_dir: Path) -> dict:
    metadata_path = version_dir / "metadata.json"
    if not metadata_path.exists():
        raise FileNotFoundError(f"Missing metadata file: {metadata_path}")
    return json.loads(metadata_path.read_text(encoding="utf-8"))


def _load_model_artifact(version_dir: Path, metadata: dict) -> object:
    artifact = metadata.get("artifact", "model.joblib")
    artifact_path = version_dir / artifact
    if not artifact_path.exists():
        raise FileNotFoundError(f"Missing model artifact: {artifact_path}")
    return joblib.load(artifact_path)


def load_model(force_reload: bool = False) -> LoadedModel:
    global _LOADED_MODEL
    with _MODEL_LOCK:
        if _LOADED_MODEL is not None and not force_reload:
            return _LOADED_MODEL

        version_dir = _resolve_version_dir()
        metadata = _load_metadata(version_dir)
        model = _load_model_artifact(version_dir, metadata)
        loaded = LoadedModel(
            version=metadata.get("version", version_dir.name),
            labels=metadata.get("labels", ["benign", "suspicious", "malicious"]),
            input_dim=int(metadata.get("input_dim", settings.embedding_fallback_dim)),
            model=model,
        )
        _LOADED_MODEL = loaded
        return loaded


def _fallback_probability_map() -> dict[str, float]:
    return {
        "benign": 0.20,
        "suspicious": 0.60,
        "malicious": 0.20,
    }


def _normalize_probability_map(probability_map: dict[str, float]) -> dict[str, float]:
    total = sum(max(0.0, float(value)) for value in probability_map.values())
    if total <= 0.0:
        return _fallback_probability_map()
    return {
        label: max(0.0, float(value)) / total
        for label, value in probability_map.items()
    }


def predict_from_features(features: list[float]) -> PredictionResult:
    try:
        loaded = load_model()
    except FileNotFoundError:
        return PredictionResult(
            label="suspicious",
            confidence=0.51,
            probability_map=_fallback_probability_map(),
            model_version="unavailable",
        )

    if len(features) != loaded.input_dim:
        return PredictionResult(
            label="suspicious",
            confidence=0.51,
            probability_map=_fallback_probability_map(),
            model_version=loaded.version,
        )

    x = np.array([features], dtype=float)
    if hasattr(loaded.model, "predict_proba"):
        proba_model = cast(ProbaModel, loaded.model)
        proba = proba_model.predict_proba(x)[0]
        best_idx = int(np.argmax(proba))
        label = (
            loaded.labels[best_idx] if best_idx < len(loaded.labels) else "suspicious"
        )
        confidence = float(proba[best_idx])
        probability_map = {
            loaded.labels[idx] if idx < len(loaded.labels) else f"class_{idx}": float(
                value
            )
            for idx, value in enumerate(proba)
        }
        return PredictionResult(
            label=label,
            confidence=confidence,
            probability_map=_normalize_probability_map(probability_map),
            model_version=loaded.version,
        )

    predict_model = cast(PredictModel, loaded.model)
    pred = predict_model.predict(x)[0]
    label = str(pred)
    base_map = {candidate: 0.1 for candidate in loaded.labels}
    if label in base_map:
        base_map[label] = 0.8
    else:
        base_map[label] = 0.8
    normalized_map = _normalize_probability_map(base_map)
    return PredictionResult(
        label=label,
        confidence=normalized_map.get(label, 0.6),
        probability_map=normalized_map,
        model_version=loaded.version,
    )
