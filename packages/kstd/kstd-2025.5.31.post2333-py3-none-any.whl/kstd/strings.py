"""Utility functions for string manipulation."""


def head(value: str, first: int = 50) -> str:
    """
    Take the first N characters of a string, replacing newlines with spaces.

    Args:
        value: The input string.
        first: Maximum number of characters to return (default: 50).

    Returns:
        A string of at most N characters with newlines replaced by spaces.

    """
    if len(value) <= first:
        return value.replace("\n", " ")

    return value[: first - 3].replace("\n", " ") + "..."
