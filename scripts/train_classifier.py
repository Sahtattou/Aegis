from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import joblib
import numpy as np
from sklearn.calibration import CalibratedClassifierCV
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT / "api") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "api"))

from app.services.blueteam.embeddings import embed
from app.services.blueteam.training_data import build_dataset

MODEL_ROOT = REPO_ROOT / "data" / "models" / "blueteam" / "classifier"


def train() -> None:
    texts, labels = build_dataset()
    if len(texts) < 3:
        raise RuntimeError("Not enough training data. Need at least 3 samples.")

    label_set = sorted(set(labels))
    if len(label_set) < 2:
        raise RuntimeError("Need at least two label classes to train classifier.")

    vectors = np.array([embed(text) for text in texts], dtype=float)
    y = np.array(labels)

    x_train, x_test, y_train, y_test = train_test_split(
        vectors,
        y,
        test_size=0.33,
        random_state=42,
        stratify=y,
    )

    base = Pipeline(
        [
            ("scaler", StandardScaler()),
            (
                "clf",
                LogisticRegression(
                    solver="lbfgs",
                    class_weight="balanced",
                    max_iter=3000,
                    C=1.0,
                ),
            ),
        ]
    )
    model = CalibratedClassifierCV(base, method="sigmoid", cv=3)
    model.fit(x_train, y_train)

    score = float(model.score(x_test, y_test))
    labels_sorted = sorted({str(label) for label in y})

    version = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
    version_dir = MODEL_ROOT / version
    version_dir.mkdir(parents=True, exist_ok=True)

    artifact_name = "model.joblib"
    artifact_path = version_dir / artifact_name
    joblib.dump(model, artifact_path)

    metadata = {
        "model_name": "blueteam-logreg-calibrated",
        "version": version,
        "framework": "scikit-learn",
        "artifact": artifact_name,
        "input_dim": int(vectors.shape[1]),
        "labels": labels_sorted,
        "created_at": datetime.now(UTC).isoformat(),
    }
    metrics = {
        "accuracy": score,
        "train_size": int(x_train.shape[0]),
        "test_size": int(x_test.shape[0]),
    }

    (version_dir / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (version_dir / "metrics.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(json.dumps({"version": version, "metrics": metrics}, ensure_ascii=False))


if __name__ == "__main__":
    train()
