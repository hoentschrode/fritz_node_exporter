"""Main function to trigger a service/action call and print return value(s)."""
from pprint import pprint
from .device import FritzBox
from .service_action import ServiceAction


def do_call(device: FritzBox, service_action: ServiceAction) -> None:
    data = device.call(service_action)
    pprint(data)
