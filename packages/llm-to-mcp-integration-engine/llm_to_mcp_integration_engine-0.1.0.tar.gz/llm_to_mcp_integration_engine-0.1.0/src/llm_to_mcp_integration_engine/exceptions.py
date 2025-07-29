class IntegrationError(Exception):
    """Base class for integration exceptions."""
    pass


class InvalidFormatError(IntegrationError):
    """Raised when the LLM response format is invalid."""
    pass


class ToolNotFoundError(IntegrationError):
    """Raised when a tool is not found in the registry."""
    pass


class RetryLimitExceededError(IntegrationError):
    """Raised when the retry limit is exceeded."""
    pass
