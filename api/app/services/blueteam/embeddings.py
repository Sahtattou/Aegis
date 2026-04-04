import hashlib
import importlib
import math
from functools import lru_cache
from pathlib import Path
from typing import Any, Protocol

from app.config import settings


class Embedder(Protocol):
    def encode(self, text: str) -> list[float]: ...


class SentenceTransformerEmbedder:
    def __init__(self) -> None:
        sentence_transformers = importlib.import_module("sentence_transformers")
        sentence_transformer_class: Any = getattr(
            sentence_transformers, "SentenceTransformer"
        )

        cache_dir = Path(settings.embedding_cache_dir)
        cache_dir.mkdir(parents=True, exist_ok=True)
        self._model = sentence_transformer_class(
            settings.embedding_model_name,
            device=settings.embedding_device,
            cache_folder=str(cache_dir),
            trust_remote_code=False,
        )

    def encode(self, text: str) -> list[float]:
        vector = self._model.encode(
            [text],
            normalize_embeddings=True,
            convert_to_numpy=True,
        )[0]
        return [float(v) for v in vector]


class DeterministicFallbackEmbedder:
    def __init__(self, dim: int) -> None:
        self._dim = dim

    def encode(self, text: str) -> list[float]:
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        values: list[float] = []
        for i in range(self._dim):
            b = digest[i % len(digest)]
            values.append((b / 255.0) * 2.0 - 1.0)
        norm = math.sqrt(sum(v * v for v in values))
        if norm == 0:
            return values
        return [v / norm for v in values]


@lru_cache(maxsize=1)
def _get_embedder() -> Embedder:
    try:
        return SentenceTransformerEmbedder()
    except Exception:
        return DeterministicFallbackEmbedder(settings.embedding_fallback_dim)


def embed(text: str) -> list[float]:
    return _get_embedder().encode(text)
