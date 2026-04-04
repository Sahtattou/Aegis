import os


class Settings:
    def __init__(self) -> None:
        self.neo4j_uri = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
        self.neo4j_username = os.getenv("NEO4J_USERNAME", "neo4j")
        self.neo4j_password = os.getenv("NEO4J_PASSWORD", "neo4jpassword")
        self.claude_api_key = os.getenv("CLAUDE_API_KEY", "")


settings = Settings()
