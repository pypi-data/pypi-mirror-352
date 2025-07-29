class RetryHandler:
    """Encapsulate retry counting, prompt-rewriting, optional model swap."""

    def __init__(self, max_attempts: int = 3):
        self.max_attempts = max_attempts
        self.attempts = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.attempts >= self.max_attempts:
            raise StopIteration
        self.attempts += 1
        return self.attempts

    def should_retry(self, error: Exception) -> bool:
        """Decide whether to retry based on the error."""
        from .exceptions import IntegrationError
        return isinstance(error, IntegrationError)

    def build_retry_prompt(self, base: str, retry_prompt: str) -> str:
        """Build a refined prompt for the next retry attempt."""
        return base + " " + retry_prompt

    def next_model(self):
        """Optionally swap to the next LLM if CHANGE_LLM_IN_RETRY is set."""
        # TODO: Implement logic to swap to the next LLM
        pass
