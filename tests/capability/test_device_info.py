"""Test device info capability."""
from fritz_node_exporter.device import FritzBox
from fritz_node_exporter.capabilities import DeviceInfo
from fritz_node_exporter.service_action import ServiceAction


def test_service_action_initialization():
    """Test initialization."""
    device_info = DeviceInfo()
    assert device_info._service_action is not None


def test_capability_supported():
    """Test supported device info.

    GIVEN Default configured fritzbox
    WHEN checking for device_info capability support
    THEN check returns true and fritzbox get's name.
    """

    class MockedFritzBox(FritzBox):
        def __init__(self, *args, **kwargs) -> None:
            pass

        def call(self, service_action: ServiceAction):
            return {
                "NewModelName": "TestFritzBox",
                "NewSoftwareVersion": "12345",
                "NewSerialNumber": "ABCDE",
            }

    fritzbox = MockedFritzBox()
    device_info = DeviceInfo()
    assert device_info.is_supported(fritzbox)
    assert fritzbox.name == "TestFritzBox"


def test_capability_not_supported():
    """Test unsupported device info.

    GIVEN Default configured fritzbox
    WHEN checking for device_info capability support
    THEN check returns False.
    """

    class MockedFritzBox(FritzBox):
        def __init__(self, *args, **kwargs) -> None:
            pass

        def call(self, service_action: ServiceAction):
            return {
                "NewSoftwareVersion": "12345",
                "NewSerialNumber": "ABCDE",
            }

    fritzbox = MockedFritzBox()
    device_info = DeviceInfo()
    assert device_info.is_supported(fritzbox) is False
