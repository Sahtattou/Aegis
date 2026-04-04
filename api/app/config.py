class Settings:
    def __init__(self) -> None:
        self.neo4j_uri = "bolt://neo4j:7687"
        self.neo4j_username = "neo4j"
        self.neo4j_password = "neo4jpassword"
        self.claude_api_key = ""


settings = Settings()
