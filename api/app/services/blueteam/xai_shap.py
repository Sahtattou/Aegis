from dataclasses import dataclass


@dataclass
class FeatureContribution:
    feature: str
    contribution: float
    direction: str


def _safe_contribution(value: float) -> float:
    if value > 10.0:
        return 10.0
    if value < -10.0:
        return -10.0
    return value


def _derive_direction(value: float) -> str:
    if value > 0:
        return "increase_risk"
    if value < 0:
        return "decrease_risk"
    return "neutral"


def compute_top_contributors(
    feature_names: list[str], feature_values: list[float], top_k: int = 5
) -> list[FeatureContribution]:
    if not feature_names or not feature_values:
        return []

    contributions: list[FeatureContribution] = []
    for name, value in zip(feature_names, feature_values, strict=False):
        contribution = _safe_contribution(float(value))
        contributions.append(
            FeatureContribution(
                feature=name,
                contribution=contribution,
                direction=_derive_direction(contribution),
            )
        )

    contributions.sort(key=lambda item: abs(item.contribution), reverse=True)
    return contributions[: max(1, top_k)]
