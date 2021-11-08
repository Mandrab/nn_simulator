# -*- coding: utf-8 -*-
import logging
import view.plot as plot

from model.analysis.evolution import Evolution
from model.analysis.measures import print_info, inspect
from model.device.datasheet.default import default
from model.device.factory import generate_network, get_graph, generate_graph
from model.device.utils import initialize_graph_attributes, largest_component
from model.stimulator import stimulate, voltage_initialization

__all__ = [
    # statistical analysis
    "Evolution",                # network-state collectors for analysis
    "print_info", "inspect",    # supervision utils
    # device utilities
    "default",                  # device data
    "generate_network", "get_graph", "generate_graph",  # network creation
    "initialize_graph_attributes", "largest_component", # network initialization
    # stimulation utilities
    "stimulate", "voltage_initialization",  # network stimulation
    # logging utilities
    "logging", "debug_mode",    # logging setups


    "plot"  # plotting utils
]

__LOGGING_FORMAT = '[%(asctime)s %(levelname)s]\t %(message)s'

# define default logging level as INFO and following a standard format
logging.basicConfig(level=logging.INFO, format=__LOGGING_FORMAT)


# enable the debug mode in the simulator (i.e., log at DEBUG level)
def debug_mode():
    logging.basicConfig(level=logging.DEBUG, format=__LOGGING_FORMAT)
