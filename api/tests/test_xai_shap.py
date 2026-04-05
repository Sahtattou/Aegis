from app.services.blueteam.xai_shap import compute_top_contributors


def test_compute_top_contributors_returns_top_k() -> None:
    names = ["f1", "f2", "f3", "f4"]
    values = [0.1, -2.0, 1.5, 0.2]
    result = compute_top_contributors(names, values, top_k=2)
    assert len(result) == 2
    assert result[0].feature in {"f2", "f3"}
    assert result[1].feature in {"f2", "f3"}


def test_compute_top_contributors_empty_input() -> None:
    assert compute_top_contributors([], []) == []
