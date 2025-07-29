class AstarError(Exception):
    """Base exception for the SDK."""


class AuthenticationError(AstarError):
    pass


class APIError(AstarError):
    def __init__(self, message: str, status: int):
        super().__init__(f"[{status}] {message}")
        self.status = status
