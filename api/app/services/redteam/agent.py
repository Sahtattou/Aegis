from importlib import import_module
from typing import Any

from app.config import settings
from app.db.repository import Repository
from app.services.redteam.personas import PERSONAS


class RedTeamAgent:
    def __init__(self, repository: Repository) -> None:
        self._repository = repository

    def run(self, payload: Any) -> Any:
        redteam_models = import_module("app.models.redteam")
        redteam_attack_candidate = getattr(redteam_models, "RedTeamAttackCandidate")
        redteam_run_response = getattr(redteam_models, "RedTeamRunResponse")
        llm_module = import_module("app.utils.llm")
        invoke_structured_attack = getattr(llm_module, "invoke_structured_attack")
        sanitize_untrusted_text = getattr(llm_module, "_sanitize_untrusted_text")

        safe_target = sanitize_untrusted_text(
            str(payload.target), fallback="generic-target"
        )
        safe_objective = sanitize_untrusted_text(
            str(payload.objective), fallback="assess defensive posture"
        )
        embedding_dim = int(getattr(settings, "embedding_fallback_dim", 384))

        attacks: list[Any] = []

        for index in range(payload.n_attacks):
            persona = PERSONAS[index % len(PERSONAS)]
            generated = invoke_structured_attack(
                persona=persona,
                target=safe_target,
                objective=safe_objective,
                dimensions=embedding_dim,
            )
            embedding = generated.embedding
            max_similarity = self._repository.max_attack_similarity(embedding)
            novelty_score = max(0.0, min(1.0, 1.0 - max_similarity))

            self._repository.create_structured_attack(
                attack_id=generated.attack_id,
                content=generated.content,
                source="redteam",
                persona=persona,
                severity=generated.severity,
                techniques=generated.techniques,
                target=safe_target,
                objective=safe_objective,
                embedding=embedding,
            )

            attacks.append(
                redteam_attack_candidate(
                    persona=persona,
                    attack_id=generated.attack_id,
                    content=generated.content,
                    severity=generated.severity,
                    techniques=generated.techniques,
                    embedding=embedding,
                    novelty_score=novelty_score,
                    max_similarity=max_similarity,
                )
            )

        return redteam_run_response(
            status="completed",
            target=safe_target,
            objective=safe_objective,
            n_attacks=payload.n_attacks,
            attacks=attacks,
        )
