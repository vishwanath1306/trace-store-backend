class SessionNotFoundException(Exception):
    def __init__(self, error: str):
        self.error = f"Session not found {error}"

    def __str__(self):
        return self.error


class VectorStoreNotFoundException(Exception):
    def __init__(self, error: str):
        self.error = f"Vector Store not found {error}"

    def __str__(self):
        return self.error
    
class RedisSetupException(Exception):
    def __init__(self, error: str):
        self.error = f"{error}"

    def __str__(self):
        return self.error
    

def RedisConnectionException(Exception):
    def __init__(self, error: str):
        self.error = f"Redis connection failed {error}"

    def __str__(self):
        return self.error

def RedisRuntimeError(Exception):
    def __init__(self, error: str):
        self.error = f"Redis runtime error {error}"

    def __str__(self):
        return self.error