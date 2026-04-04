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


def predict_from_features(features: list[float]) -> tuple[str, float]:
    try:
        loaded = load_model()
    except FileNotFoundError:
        return ("suspicious", 0.51)

    if len(features) != loaded.input_dim:
        return ("suspicious", 0.51)

    x = np.array([features], dtype=float)
    if hasattr(loaded.model, "predict_proba"):
        proba_model = cast(ProbaModel, loaded.model)
        proba = proba_model.predict_proba(x)[0]
        best_idx = int(np.argmax(proba))
        label = (
            loaded.labels[best_idx] if best_idx < len(loaded.labels) else "suspicious"
        )
        confidence = float(proba[best_idx])
        return (label, confidence)

    predict_model = cast(PredictModel, loaded.model)
    pred = predict_model.predict(x)[0]
    return (str(pred), 0.6)
