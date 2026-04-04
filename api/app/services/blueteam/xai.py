def explain_french(decision: str, confidence: float, evidence: list[str]) -> str:
    joined = "; ".join(evidence) if evidence else "aucune preuve contextuelle"
    return (
        f"Décision: {decision}. "
        f"Confiance: {confidence:.2f}. "
        f"Éléments clés: {joined}."
    )