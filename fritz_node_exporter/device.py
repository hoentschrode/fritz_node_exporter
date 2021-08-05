"""Define a single fritz device."""
from __future__ import annotations
from typing import Optional, List, Dict, Iterable
import logging

from fritzconnection import FritzConnection
from fritzconnection.core.exceptions import FritzActionError, FritzServiceError
from prometheus_client.metrics_core import Metric
from requests.exceptions import ConnectionError

from .config import DeviceConfig
from .exception import CallException
from .capability import Capability
from fritz_node_exporter.capabilities import ALL_CAPABILITIES
from .service_action import ServiceAction

logger = logging.getLogger(__name__)


class FritzBox:
    """Describe a single Fritz!Box."""

    def __init__(self, config: DeviceConfig, skip_capability_discovery=False) -> None:
        """Initialize..."""
        self._device_config = config
        self._fritz_connection: Optional[FritzConnection] = None
        self._capabilities: List[Capability] = list()
        self._name = self._device_config.hostname
        self._swversion: str = "UNKNOWN"
        self._serialno: str = "UNKNOWN"

        self._connect()
        if not skip_capability_discovery:
            self._discover_capabilities()

    def call(self, service_action: ServiceAction) -> Optional[Dict[str, str]]:
        """Send service/action to Fritz!Box. Might raise Exceptions."""
        if self._fritz_connection is None:
            logger.error(
                "Not connected to Fritz!Box {} anymore!".format(
                    self._device_config.name
                )
            )
            return None
        try:
            logger.debug(
                "Call service {}, action {} on {}...".format(
                    service_action.service,
                    service_action.action,
                    self._device_config.hostname,
                )
            )
            result = self._fritz_connection.call_action(
                service_action.service, service_action.action
            )
            return result
        except (FritzServiceError, FritzActionError) as e:
            logger.error(
                "Error executing {}/{} on {}: {}".format(
                    service_action.service,
                    service_action.action,
                    self._device_config.hostname,
                    str(e),
                )
            )
            raise CallException(e)

    def _connect(self):
        try:
            logger.info(
                "Establishing connection to {}...".format(self._device_config.hostname)
            )
            self._fritz_connection = FritzConnection(
                address=self._device_config.hostname,
                user=self._device_config.username,
                password=self._device_config.password,
            )
        except ConnectionError as e:
            logger.exception(
                "Failed to connect to Fritz!Box {}: {}".format(
                    self._device_config.hostname, str(e)
                ),
                exc_info=True,
            )
            raise e
        logger.info(
            "Connected to Fritz!Box {}. Discovering capabilities...".format(
                self._device_config.hostname
            )
        )

    def _discover_capabilities(self):
        """Check wich capabilities are provided by this device."""
        for capability_cls in ALL_CAPABILITIES:
            capability = capability_cls()
            if capability.is_supported(self):
                logger.info(
                    "Capability {} successfully discovered on {}.".format(
                        capability.__class__.__name__, self._device_config.hostname
                    )
                )
                self._capabilities.append(capability)
            else:
                logger.info(
                    "Capability {} not supported by {}. Metric(s) skipped too.".format(
                        capability.__class__.__name__, self._device_config.hostname
                    )
                )

    @property
    def name(self) -> str:
        """Retrieve name after discovery."""
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        """Setter for device name."""
        self._name = name

    @property
    def swversion(self) -> str:
        """Getter for software version."""
        return self._swversion

    @swversion.setter
    def swversion(self, swversion: str) -> None:
        """Setter for sofware version."""
        self._swversion = swversion

    @property
    def serialno(self) -> str:
        """Getter for serial number."""
        return self._serialno

    @serialno.setter
    def serialno(self, serialno: str) -> None:
        """Setter for serial number."""
        self._serialno = serialno

    @property
    def capabilities(self) -> List[Capability]:
        """Getter for all discovered capabilities."""
        return self._capabilities

    @property
    def has_capabilities(self) -> bool:
        """Return true if device has at least one capability."""
        return len(self._capabilities) > 0

    def get_all_metric_values(self) -> Iterable[Metric]:
        for capability in self._capabilities:
            yield from capability.get_metrics(self)


class FritzBoxCollection:
    def __init__(self) -> None:
        self._fritz_boxes: List[FritzBox] = list()

    def add(self, device: FritzBox):
        if device.has_capabilities:
            logger.debug("Adding device {} to collection.".format(device.name))
            self._fritz_boxes.append(device)
        else:
            logger.error(
                "Device {} has no discovered capabilities. Not adding to collection".format(
                    device.name
                )
            )

    def collect(self) -> Metric:
        for device in self._fritz_boxes:
            yield from device.get_all_metric_values()
