class BaseExceptionWithMetadata(Exception):
    def __init__(self, message: str, metadata: dict = {}):
        super().__init__(message)
        self.metadata = metadata
