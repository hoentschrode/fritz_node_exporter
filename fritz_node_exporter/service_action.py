from dataclasses import dataclass


@dataclass
class ServiceAction:
    """Define a Fritz Service together with action."""

    service: str
    action: str
