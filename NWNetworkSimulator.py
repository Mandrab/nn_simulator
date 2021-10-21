# -*- coding: utf-8 -*-

# standard lib
import logging

# project files
from model import NetworkUtils
from model.device.default import default
from model.inspect import print_info, inspect, information_centrality
from model.NetworkStimulator import NetworkStimulator

# from view.view import plot_all


def enable_logging(
        level=logging.INFO,
        format='[%(asctime)s %(levelname)s]\t %(message)s'
):
    logging.basicConfig(level=level, format=format)


enable_logging()

__all__ = [
    "logging",
    "NetworkUtils",
    "default",
    "print_info", "inspect", "information_centrality",
    "NetworkStimulator",
    "enable_logging"
]
