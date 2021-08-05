"""Module containing all capabilities."""
from .device_info import DeviceInfo
from .wan_dsl_info import WanDslInfo

# Expose list of all available capabilities
ALL_CAPABILITIES = [DeviceInfo, WanDslInfo]
