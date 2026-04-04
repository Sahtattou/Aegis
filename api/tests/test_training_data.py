from app.services.blueteam.training_data import build_dataset, load_training_samples


def test_training_samples_load() -> None:
    samples = load_training_samples()
    assert len(samples) > 0


def test_dataset_shapes_match() -> None:
    texts, labels = build_dataset()
    assert len(texts) == len(labels)
    assert len(texts) > 0
