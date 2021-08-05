"""Get basic device info."""
from __future__ import annotations
import logging
from typing import TYPE_CHECKING, Iterable, Optional
from dataclasses import dataclass
from prometheus_client.core import CounterMetricFamily
from ..capability import Capability
from ..service_action import ServiceAction
from ..exception import CallException
from ..utils import safe_str_to_int

if TYPE_CHECKING:
    from ..device import FritzBox

logger = logging.getLogger(__name__)


@dataclass
class MetricData:
    """Holds metric relevant data."""

    modelname: Optional[str]
    swversion: Optional[str]
    serial_no: Optional[str]
    uptime: int

    def any_is_none(self) -> bool:
        """Determine if any of the atttributes is None."""
        return (
            self.modelname is None or self.swversion is None or self.serial_no is None
        )


class DeviceInfo(Capability):
    """Device informations."""

    def __init__(self) -> None:
        """Initialize capability."""
        super().__init__()
        self._service_action = ServiceAction(service="DeviceInfo1", action="GetInfo")
        self._metric = None

    def is_supported(self, device: FritzBox) -> bool:
        """Check if device supports DeviceInfo."""
        try:
            logger.info("Checking {} support..".format(self.__class__.__name__))
            metric_data = self._query(device)
            if metric_data is None or metric_data.any_is_none():
                return False
            logger.debug("Setting device name to {}".format(metric_data.modelname))
            device.name = str(metric_data.modelname)
            device.swversion = str(metric_data.swversion)
            device.serialno = str(metric_data.serial_no)
            return True
        except CallException:
            return False

    def get_metrics(self, device: FritzBox) -> Iterable[CounterMetricFamily]:
        """Query device and yield metric data."""
        metric = CounterMetricFamily(
            "fritz_uptime",
            "Fritz!Box uptime",
            labels=["modelname", "softwareversion", "serialno"],
            unit="seconds",
        )

        try:
            logger.debug("Query for device info...")
            metric_data = self._query(device)
            if metric_data is None:
                return None
            metric.add_metric(
                [metric_data.modelname, metric_data.swversion, metric_data.serial_no],
                metric_data.uptime,
            )
            yield metric
        except Exception:
            return None

    def _query(self, device: FritzBox) -> Optional[MetricData]:
        """Query metric relevant data."""
        try:
            data = device.call(self._service_action)
            if data is None:
                return None
            return MetricData(
                modelname=data.get("NewModelName"),
                swversion=data.get("NewSoftwareVersion"),
                serial_no=data.get("NewSerialNumber"),
                uptime=safe_str_to_int(str(data.get("NewUpTime"))),
            )
        except CallException:
            return None
