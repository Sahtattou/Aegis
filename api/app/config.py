import os
from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings:
    def __init__(self) -> None:
        self.neo4j_uri = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
        self.neo4j_username = os.getenv("NEO4J_USERNAME", "neo4j")
        self.neo4j_password = os.getenv("NEO4J_PASSWORD", "neo4jpassword")
        self.claude_api_key = os.getenv("CLAUDE_API_KEY", "")
        self.redteam_vector_index_name = os.getenv("REDTEAM_VECTOR_INDEX_NAME", "attack_embedding_index")
        self.redteam_vector_dimensions = int(os.getenv("REDTEAM_VECTOR_DIMENSIONS", "768"))
        self.neo4j_init_on_startup = os.getenv("NEO4J_INIT_ON_STARTUP", "true").lower() == "true"
        default_init_dir = Path(__file__).resolve().parent / "db" / "cypher_init"
        self.neo4j_init_dir = os.getenv("NEO4J_INIT_DIR", str(default_init_dir))
        self.embedding_model_name = os.getenv(
            "EMBEDDING_MODEL_NAME",
            "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        )
        self.embedding_device = os.getenv("EMBEDDING_DEVICE", "cpu")
        self.embedding_cache_dir = os.getenv("EMBEDDING_CACHE_DIR", "/app/data/models")
        self.embedding_fallback_dim = int(os.getenv("EMBEDDING_FALLBACK_DIM", "384"))

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    neo4j_uri: str = "bolt://neo4j:7687"
    neo4j_username: str = "neo4j"
    neo4j_password: str = "neo4jpassword"

    claude_api_key: str = ""

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
