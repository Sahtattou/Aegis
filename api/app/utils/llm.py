import json
from dataclasses import dataclass
from hashlib import sha256
from importlib import import_module


@dataclass(frozen=True)
class StructuredAttackPayload:
    attack_id: str
    content: str
    severity: str
    techniques: list[str]
    embedding: list[float]


def _embedding_from_seed(seed: str, dimensions: int = 16) -> list[float]:
    digest = sha256(seed.encode("utf-8")).digest()
    values: list[float] = []
    for index in range(dimensions):
        byte_value = digest[index % len(digest)]
        values.append(byte_value / 255.0)
    return values


def _render_prompt(persona: str, target: str, objective: str) -> str:
    template = """
You are a red-team simulation assistant.
Persona: {persona}
Target: {target}
Objective: {objective}

Produce a concise simulation scenario and the likely tactics.
""".strip()
    try:
        prompts_module = import_module("langchain.prompts")
        prompt_template = prompts_module.PromptTemplate.from_template(template)
        return prompt_template.format(persona=persona, target=target, objective=objective)
    except Exception:
        return template.format(persona=persona, target=target, objective=objective)


def invoke_structured_attack(*, persona: str, target: str, objective: str, dimensions: int = 16) -> StructuredAttackPayload:
    rendered_prompt = _render_prompt(persona, target, objective)
    attack_seed = f"{persona}|{target}|{objective}|{rendered_prompt}"
    attack_hash = sha256(attack_seed.encode("utf-8")).hexdigest()

    if "Phishing" in persona:
        techniques = ["spear-phishing", "credential-harvest"]
        severity = "high"
    elif "Credential" in persona:
        techniques = ["credential-stuffing", "account-takeover"]
        severity = "medium"
    else:
        techniques = ["pretexting", "vishing"]
        severity = "medium"

    payload = {
        "attack_id": f"atk-{attack_hash[:12]}",
        "content": (
            f"{persona} targets {target} to {objective}. "
            f"Simulated path uses {', '.join(techniques)} with staged social pressure."
        ),
        "severity": severity,
        "techniques": techniques,
        "embedding": _embedding_from_seed(attack_seed, dimensions=dimensions),
    }

    serialized = json.dumps(payload)
    parsed = json.loads(serialized)

    return StructuredAttackPayload(
        attack_id=str(parsed["attack_id"]),
        content=str(parsed["content"]),
        severity=str(parsed["severity"]),
        techniques=[str(item) for item in parsed["techniques"]],
        embedding=[float(item) for item in parsed["embedding"]],
    )
