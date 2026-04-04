import importlib


def dataset_summary() -> dict[str, int]:
    module = importlib.import_module("app.services.blueteam.training_data")
    build_dataset = getattr(module, "build_dataset")
    texts, labels = build_dataset()
    malicious = sum(1 for label in labels if label == "malicious")
    benign = sum(1 for label in labels if label == "benign")
    suspicious = sum(1 for label in labels if label == "suspicious")
    return {
        "samples": len(texts),
        "malicious": malicious,
        "benign": benign,
        "suspicious": suspicious,
    }
