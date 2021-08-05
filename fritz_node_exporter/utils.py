"""Several utility functions."""
from typing import Optional


def safe_str_to_int(s: Optional[str], default_value: int = 0) -> int:
    """Convert str to int. Return default_value on any problem."""
    if s is None:
        return default_value

    try:
        v = int(s)
    except ValueError:
        v = default_value
    return v
