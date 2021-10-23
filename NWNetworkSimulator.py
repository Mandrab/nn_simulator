# -*- coding: utf-8 -*-

# standard lib
import logging
import model.device.devices as devices

# project files
from model.device.default import default
from model.inspect import print_info, inspect, information_centrality
from model.NetworkStimulator import NetworkStimulator

# from view.view import plot_all


__LOGGING_FORMAT = '[%(asctime)s %(levelname)s]\t %(message)s'
__all__ = [
    "logging", "debug_mode",    # logging utils
    "default", "devices",       # device utils
    "print_info", "inspect", "information_centrality",
    "NetworkStimulator"         # simulator
]

logging.basicConfig(level=logging.INFO, format=__LOGGING_FORMAT)


def debug_mode():
    logging.basicConfig(level=logging.DEBUG, format=__LOGGING_FORMAT)
