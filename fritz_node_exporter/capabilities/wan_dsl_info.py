"""Get WAN/DSL informations."""
from __future__ import annotations
from fritz_node_exporter.exception import CallException
from typing import TYPE_CHECKING, Iterable, Optional
import logging
from dataclasses import dataclass

from prometheus_client.core import GaugeMetricFamily
from ..capability import Capability
from ..service_action import ServiceAction
from ..utils import safe_str_to_int

if TYPE_CHECKING:
    from ..device import FritzBox

logger = logging.getLogger(__name__)


@dataclass
class MetricData:
    dsl_is_up: bool
    downstream_current_rate: int
    downstream_max_rate: int
    upstream_current_rate: int
    upstream_max_rate: int


class WanDslInfo(Capability):
    """WAN & DSL informatins."""

    def __init__(self) -> None:
        self._service_action = ServiceAction(
            service="WANDSLInterfaceConfig1", action="GetInfo"
        )

    def is_supported(self, device: FritzBox) -> bool:
        """Check if FritzBox supports WAN info."""
        try:
            logger.info("Checking {} support...".format(self.__class__.__name__))
            metric_data = self._query(device)
            return metric_data is not None
        except CallException:
            return False

    def get_metrics(self, device: FritzBox) -> Iterable[GaugeMetricFamily]:
        """Create counter and gauges."""
        metric_dsl_enabled = GaugeMetricFamily(
            "fritz_dsl_enabled",
            "Fritz!Box DSL enabled",
            labels=["modelname", "softwareversion", "serialno"],
        )
        metric_dsl_rate = GaugeMetricFamily(
            "fritz_dsl_rate",
            "Fritz!Box DSL data rate",
            labels=[
                "modelname",
                "softwareversion",
                "serialno",
                "direction",
                "type",
            ],
            unit="kbps",
        )
        try:
            logger.debug("Query for WAN/DSL info...")
            metric_data = self._query(device)
            if metric_data is None:
                return None

            # DSL on/off
            metric_dsl_enabled.add_metric(
                [device.name, device.swversion, device.serialno],
                1 if metric_data.dsl_is_up else 0,
            )

            # DSL upstream bandwidth
            metric_dsl_rate.add_metric(
                [device.name, device.swversion, device.serialno, "up", "current"],
                metric_data.upstream_current_rate,
            )
            metric_dsl_rate.add_metric(
                [device.name, device.swversion, device.serialno, "up", "max"],
                metric_data.upstream_max_rate,
            )

            # DSL downstream bandwidth
            metric_dsl_rate.add_metric(
                [device.name, device.swversion, device.serialno, "down", "current"],
                metric_data.downstream_current_rate,
            )
            metric_dsl_rate.add_metric(
                [device.name, device.swversion, device.serialno, "down", "max"],
                metric_data.downstream_max_rate,
            )

            yield metric_dsl_enabled
            yield metric_dsl_rate
        except Exception:
            return None

    def _query(self, device: FritzBox) -> Optional[MetricData]:
        try:
            data = device.call(self._service_action)
            if data is None:
                return None

            return MetricData(
                dsl_is_up=data.get("NewStatus") == "Up",
                downstream_current_rate=safe_str_to_int(
                    data.get("NewDownstreamCurrRate")
                ),
                downstream_max_rate=safe_str_to_int(data.get("NewDownstreamMaxRate")),
                upstream_current_rate=safe_str_to_int(data.get("NewUpstreamCurrRate")),
                upstream_max_rate=safe_str_to_int(data.get("NewUpstreamMaxRate")),
            )
        except CallException:
            return None
