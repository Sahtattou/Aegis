from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    neo4j_uri: str = "bolt://neo4j:7687"
    neo4j_username: str = "neo4j"
    neo4j_password: str = "neo4jpassword"
    neo4j_connection_timeout_seconds: float = 1.0
    neo4j_acquisition_timeout_seconds: float = 1.0

    claude_api_key: str = ""

    redteam_vector_index_name: str = "attack_embedding_index"
    redteam_vector_dimensions: int = 768
    neo4j_init_on_startup: bool = True
    neo4j_init_dir: str = "/app/app/db/cypher_init"

    embedding_model_name: str = (
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )
    embedding_device: str = "cpu"
    embedding_cache_dir: str = "data/models/cache"
    embedding_fallback_dim: int = 384

    classifier_model_root: str = "data/models/blueteam/classifier"
    classifier_active_version: str = "latest"

    allowed_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:5173"]
    )
    trusted_hosts: list[str] = Field(
        default_factory=lambda: ["localhost", "127.0.0.1", "gateway", "testserver"]
    )
    internal_api_key: str = ""


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    cache_dir = Path(settings.embedding_cache_dir)
    if not cache_dir.is_absolute():
        cache_dir = Path(__file__).resolve().parents[2] / cache_dir
    cache_dir.mkdir(parents=True, exist_ok=True)
    settings.embedding_cache_dir = str(cache_dir)
    return settings


settings = get_settings()
