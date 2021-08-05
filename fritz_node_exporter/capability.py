"""Single basic capability."""
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Iterable
from abc import ABC, abstractmethod
from prometheus_client.core import Metric

if TYPE_CHECKING:
    from fritz_node_exporter.device import FritzBox


class Capability(ABC):
    """Base class for any capability."""

    def __init__(self) -> None:
        """Initialize new capability."""
        super().__init__()

    @abstractmethod
    def is_supported(self, device: FritzBox) -> bool:
        """Check if capability is supported by FritzBox."""
        pass

    @abstractmethod
    def get_metrics(self, device: FritzBox) -> Iterable[Metric]:
        """Fetch values and yield metrics."""
        pass
