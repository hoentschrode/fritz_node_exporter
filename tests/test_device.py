"""Test device class."""
import pytest
from typing import Dict

from requests.exceptions import ConnectionError

import fritz_node_exporter.device
from fritz_node_exporter.config import DeviceConfig
from fritz_node_exporter.device import FritzBox
from fritz_node_exporter.service_action import ServiceAction
from fritz_node_exporter.exception import CallException


def test_non_connectable_device():
    """Check something blablbla.

    GIVEN A non-connectable fritzbox (unrachable hostnname).
    WHEN initializing FritzBox
    THEN a connection error exception is thrown
    """
    default_config = DeviceConfig()
    default_config.hostname = "non.connectable.hostname.com"
    with pytest.raises(ConnectionError):
        FritzBox(default_config)


def test_call_disconnected_device(monkeypatch: pytest.MonkeyPatch):
    """Call a service/action on a disconnected device.

    GIVEN Default configured FritzBox
    WHEN calling service/action
    THEN call returnes None
    """

    class MockFritzConnection:
        """Mocked FritzConnection."""

        def __init__(self, *args, **kwargs) -> None:
            pass

        def call_action(self, service: str, action: str) -> None:
            pass

    monkeypatch.setattr(
        fritz_node_exporter.device, "FritzConnection", MockFritzConnection
    )
    fritzbox = FritzBox(DeviceConfig())
    fritzbox._fritz_connection = None  # Simulate disconnection
    dummy_service_action = ServiceAction(service="dummy", action="dummy")
    response = fritzbox.call(dummy_service_action)
    assert response is None


def test_call_invalid_service(monkeypatch: pytest.MonkeyPatch):
    """Call invalid service.

    GIVEN Default configured FritzBox
    WHEN calling an invalid service
    THEN an exception is raised
    """

    class MockFritzConnectionRaisesServiceException:
        """Mocked FritzConnection."""

        def __init__(self, *args, **kwargs) -> None:
            pass

        def call_action(self, service: str, action: str) -> None:
            raise CallException()

    monkeypatch.setattr(
        fritz_node_exporter.device,
        "FritzConnection",
        MockFritzConnectionRaisesServiceException,
    )
    fritzbox = FritzBox(DeviceConfig())
    with pytest.raises(CallException):
        fritzbox.call(ServiceAction(service="invalid service", action="some action"))


def test_call_invalid_action(monkeypatch: pytest.MonkeyPatch):
    """Call an invalid action.

    GIVEN Default configured FritzBox
    WHEN calling an invalid action
    THEN an exception is raised.
    """

    class MockFritzConnectionRaisesActionException:
        def __init__(self, *args, **kwargs) -> None:
            pass

        def call_action(self, service: str, action: str) -> None:
            raise CallException()

    monkeypatch.setattr(
        fritz_node_exporter.device,
        "FritzConnection",
        MockFritzConnectionRaisesActionException,
    )
    fritzbox = FritzBox(DeviceConfig())
    with pytest.raises(CallException):
        fritzbox.call(ServiceAction("some service", action="invalid action"))


def test_failed_discovery(monkeypatch: pytest.MonkeyPatch):
    """Test fritzbox after failed discovery.

    GIVEN Default configured FritzBox
    WHEN no capability was discovered
    THEN list of capabilities is empty.
    """

    class MockFritzConnection:
        def __init__(self, *args, **kwargs) -> None:
            pass

        def call_action(self, service: str, action: str) -> Dict[str, str]:
            return {}

    monkeypatch.setattr(
        fritz_node_exporter.device, "FritzConnection", MockFritzConnection
    )
    fritzbox = FritzBox(DeviceConfig())
    assert len(fritzbox.capabilities) == 0


def test_skip_discovery(monkeypatch: pytest.MonkeyPatch):
    """Test fritzbox after skipped discovery.

    GIVEN
    WHEN
    THEN
    """

    class MockFritzConnection:
        def __init__(self, *args, **kwargs) -> None:
            pass

        def call_action(self, service: str, action: str) -> Dict[str, str]:
            """Pretend to be a discovered capability."""
            if service == "DeviceInfo1" and action == "GetInfo":
                return {
                    "NewModelName": "MockedFritzBox",
                    "NewSoftwareVersion": "v1.2.3.4",
                    "NewSerialNumber": "ABCDE",
                }
            return {}

    monkeypatch.setattr(
        fritz_node_exporter.device, "FritzConnection", MockFritzConnection
    )
    fritz_box = FritzBox(DeviceConfig(), skip_capability_discovery=True)
    assert len(fritz_box.capabilities) == 0


def test_name_after_discovery(monkeypatch: pytest.MonkeyPatch):
    """Test FritzBox after successfully discovery.

    GIVEN Default configured FritzBox
    WHEN discovery was successfull
    THEN fritzbox name is set to name from discovery
    """

    class MockFritzConnection:
        def __init__(self, *args, **kwargs) -> None:
            pass

        def call_action(self, service: str, action: str) -> Dict[str, str]:
            if service == "DeviceInfo1" and action == "GetInfo":
                return {
                    "NewModelName": "MockedFritzBox",
                    "NewSoftwareVersion": "v1.2.3.4",
                    "NewSerialNumber": "ABCDE",
                }
            return {}

    monkeypatch.setattr(
        fritz_node_exporter.device, "FritzConnection", MockFritzConnection
    )
    fritzbox = FritzBox(DeviceConfig())
    assert fritzbox.name == "MockedFritzBox"
