import json
import csv
from pathlib import Path

from pydantic import BaseModel, Field


class TrainingSample(BaseModel):
    id: str
    content_text: str
    label: str
    language: str
    source: str


def load_training_samples() -> list[TrainingSample]:
    repo_root = Path(__file__).resolve().parents[4]
    dataset_path = repo_root / "api" / "data" / "datasets" / "tunisian_attacks.json"
    csv_path = repo_root / "data" / "dataset" / "tn_curated_300.csv"

    samples: list[TrainingSample] = []

    if csv_path.exists():
        with csv_path.open("r", encoding="utf-8", newline="") as file_handle:
            reader = csv.DictReader(file_handle)
            for row in reader:
                label = row.get("label", "benign")
                normalized_label = "malicious" if label == "phishing" else "benign"
                samples.append(
                    TrainingSample(
                        id=row.get("id", ""),
                        content_text=row.get("text", ""),
                        label=normalized_label,
                        language=row.get("language", "unknown"),
                        source=row.get("source_tag", "dataset"),
                    )
                )

    if dataset_path.exists():
        raw = json.loads(dataset_path.read_text(encoding="utf-8"))
        for item in raw:
            label = item.get("label", "benign")
            if label == "phishing":
                normalized_label = "malicious"
            elif label == "benign":
                normalized_label = "benign"
            else:
                normalized_label = "suspicious"

            samples.append(
                TrainingSample(
                    id=item["id"],
                    content_text=item["content_text"],
                    label=normalized_label,
                    language=item.get("language", "unknown"),
                    source=item.get("source", "dataset"),
                )
            )

    return samples


def build_dataset() -> tuple[list[str], list[str]]:
    samples = load_training_samples()
    return (
        [sample.content_text for sample in samples],
        [sample.label for sample in samples],
    )
