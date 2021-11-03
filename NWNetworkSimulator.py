# -*- coding: utf-8 -*-
import logging
import view.plot as plot

from model.device.Device import Device
from model.device.datasheet.default import default
from model.tools.inspect import print_info, inspect
from model.network.Stimulator import Stimulator

__LOGGING_FORMAT = '[%(asctime)s %(levelname)s]\t %(message)s'
__all__ = [
    "logging", "debug_mode",  # logging utils
    "default", "Device",  # device data
    "print_info", "inspect",  # supervision utils
    "Stimulator",  # network simulator
    "plot"  # plotting utils
]

# define default logging level as INFO and following a standard format
logging.basicConfig(level=logging.INFO, format=__LOGGING_FORMAT)


# enable the debug mode in the simulator (i.e., log at DEBUG level)
def debug_mode():
    logging.basicConfig(level=logging.DEBUG, format=__LOGGING_FORMAT)
