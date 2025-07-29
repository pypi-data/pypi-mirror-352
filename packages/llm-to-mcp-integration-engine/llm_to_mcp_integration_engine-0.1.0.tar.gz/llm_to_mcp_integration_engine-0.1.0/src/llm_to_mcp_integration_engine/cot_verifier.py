def verify_chain_of_thought(text: str) -> bool:
    """Enforce non-empty Chain-of-Thought."""
    if not text:
        return False
    words = text.split()
    return len(words) > 5
