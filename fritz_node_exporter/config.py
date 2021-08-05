"""Configuration holder/parser."""

import logging
from typing import List
from dataclasses import dataclass, field
from dataclasses_json import DataClassJsonMixin
from yamldataclassconfig.config import YamlDataClassConfig

logger = logging.getLogger("fritz_node_exporter.config")


@dataclass
class DeviceConfig(DataClassJsonMixin):
    """Configuration of a single device."""

    name: str = "MyFritz!Box"
    hostname: str = "fritz.box"
    username: str = "fritz"
    password: str = "box"


@dataclass
class Config(YamlDataClassConfig):
    """Main configuration."""

    port_no: int = 8888
    devices: List[DeviceConfig] = field(default_factory=list)
