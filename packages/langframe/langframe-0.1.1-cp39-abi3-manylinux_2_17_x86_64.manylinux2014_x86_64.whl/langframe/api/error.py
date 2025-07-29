
class InvalidExampleCollectionError(Exception):
    """Exception raised when a semantic example collection is invalid."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
