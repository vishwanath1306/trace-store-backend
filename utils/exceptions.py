class SessionNotFoundException(Exception):
    def __init__(self, error: str):
        self.error = f"Session not found {error}"

    def __str__(self):
        return self.error