import os
from pathlib import Path


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


settings = Settings()
