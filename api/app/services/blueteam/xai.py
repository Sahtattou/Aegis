def explain_french(decision: str, confidence: float, evidence: list[str]) -> str:
    joined = "; ".join(evidence) if evidence else "aucune preuve contextuelle"
    return (
        f"Décision: {decision}. Confiance: {confidence:.2f}. Éléments clés: {joined}."
    )


def explain_french_analyst(
    *,
    decision: str,
    confidence: float,
    evidence: list[str],
    top_contributors: list[dict[str, float | str]],
    rule_rationale: str | None,
    rule_approved_by: str | None,
) -> tuple[str, dict[str, str | float | list[str]]]:
    joined = "; ".join(evidence) if evidence else "aucune preuve contextuelle"
    contributors = [
        f"{item.get('feature', 'unknown')}={float(item.get('contribution', 0.0)):.2f}"
        for item in top_contributors
    ]
    contributors_text = ", ".join(contributors) if contributors else "aucun"

    rule_part = ""
    if rule_rationale:
        rule_part = f" Règle: {rule_rationale}."
        if rule_approved_by:
            rule_part += f" Approuvée par: {rule_approved_by}."

    explanation = (
        f"Décision: {decision}. "
        f"Confiance fusionnée: {confidence:.2f}. "
        f"Signaux principaux: {contributors_text}. "
        f"Preuves: {joined}."
        f"{rule_part}"
    )

    machine = {
        "decision": decision,
        "fused_confidence": confidence,
        "evidence": evidence,
        "top_features": contributors,
        "rule_rationale": rule_rationale or "",
        "rule_approved_by": rule_approved_by or "",
    }
    return explanation, machine
