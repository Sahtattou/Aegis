class Repository:
    def health(self) -> dict[str, str]:
        return {"db": "ready"}
