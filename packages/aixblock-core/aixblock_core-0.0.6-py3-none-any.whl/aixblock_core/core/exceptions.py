class ApplicationError(Exception):
    """Base class for application-specific exceptions.

    This class represents an error that occurs within the application's
    execution. It is intended to be used as a base class for more specific
    application-related exceptions.

    """
    def __init__(self, message, extra=None):
        super().__init__(message)

        self.message = message
        self.extra = extra or {}
