"""Main file for node exporter."""
import argparse
import logging
import logging.handlers
import os
import sys
import asyncio

from prometheus_client import start_http_server
from prometheus_client.core import REGISTRY
from marshmallow.exceptions import ValidationError

from fritz_node_exporter import CONFIG
from fritz_node_exporter.device import FritzBox, FritzBoxCollection
from fritz_node_exporter.service_action import ServiceAction
from fritz_node_exporter.call_helper import do_call

DEFAULT_LOG_FILE = os.path.join(os.path.dirname(__file__), "../fritz_node_exporter.log")
DEFAULT_LOG_SIZE = 64 * 1000000


def _setup_logging():
    root_logger = logging.getLogger("")
    root_logger.setLevel(logging.INFO)

    logfile_name = DEFAULT_LOG_FILE

    handler = logging.handlers.RotatingFileHandler(
        filename=logfile_name, maxBytes=DEFAULT_LOG_SIZE, backupCount=7
    )
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s %(module)-20s %(funcName)20s() %(message)s",
            datefmt="%m/%d/%Y %I:%M:%S %p",
        )
    )
    root_logger.addHandler(handler)


_setup_logging()
logger = logging.getLogger("fritz_node_exporter")


parser = argparse.ArgumentParser(
    description="Fritz!Box node exporter for Fritz!Box protocol",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)
parser.add_argument(
    "--config",
    type=str,
    default="./fritz_node_exporter.yml",
    help="Path and name for config file",
)
parser.add_argument(
    "--log-level",
    default="INFO",
    choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    help="Set log level",
)
parser.add_argument("--device", type=str, help="Select device (for --call argument)")
parser.add_argument("--call", type=str, help="Call 'service/action and print values")
args = parser.parse_args()

if args.log_level:
    log_level = getattr(logging, args.log_level)
    logger.info("Applying log level {} (according to config).".format(args.log_level))
    # loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
    # for log in loggers:
    #    log.setLevel(log_level)
    logger.setLevel(log_level)

if (not args.call and args.device) or (args.call and not args.device):
    print("Please specify both, --call and --device to do a call!")
    sys.exit(-1)

config_file_path = "./fritz_node_exporter.yml"
logger.info("Loading configuration file {}".format(config_file_path))
try:
    CONFIG.load(config_file_path)
except ValidationError as e:
    print("Error parsing config file! See logs for details")
    logger.exception(e)
    sys.exit(-1)
print("Config loaded")

if args.device and args.call:
    call_args = args.call.split("/")
    if len(call_args) != 2:
        print("Specify service and action to call like SERVICE_NAME/CALL_NAME.")
        sys.exit(-1)

    print(args.device)
    for device_config in CONFIG.devices:
        if device_config.name == args.device:
            print("Configuring device {}".format(device_config.name))
            fritz_box = FritzBox(device_config, skip_capability_discovery=True)
            service_action = ServiceAction(service=call_args[0], action=call_args[1])
            do_call(fritz_box, service_action)
    sys.exit(0)

fritz_box_collection = FritzBoxCollection()
for device_config in CONFIG.devices:
    fb = FritzBox(device_config)
    fritz_box_collection.add(fb)

logger.info("Starting webserver on port {}".format(CONFIG.port_no))
REGISTRY.register(fritz_box_collection)
start_http_server(CONFIG.port_no)
loop = asyncio.get_event_loop()
try:
    loop.run_forever()
finally:
    loop.close()
