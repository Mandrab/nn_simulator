# -*- coding: utf-8 -*-
from .controller import backup
from .model.analysis.evolution import Evolution
from .model.analysis.measures import print_info, inspect
from .model.device.datasheet.Datasheet import default
from .model.device.factory import generate_network, get_graph, generate_graph
from .model.device.factory import minimum_viable_network
from .model.device.utils import initialize_graph_attributes, largest_component
from .model.interface.factory import random_nodes, random_loads
from .model.interface.evolutor import mutate, non_ground_selection
from .model.interface.evolutor import minimum_distance_selection
from .model.stimulator import stimulate, voltage_initialization
from .view import plot

LOGGER_NAME = 'nanowire-network-simulator-lib'

__all__ = [
    # file system interactions
    "backup",
    # statistical analysis
    "Evolution",                # network-state collectors for analysis
    "print_info", "inspect",    # supervision utils
    # device utilities & configurations
    "default",
    # network creation
    "generate_network", "get_graph", "generate_graph", "minimum_viable_network",
    # network initialization
    "initialize_graph_attributes", "largest_component",
    # interface / connection definition
    "random_nodes", "random_loads", "mutate", "non_ground_selection",
    "minimum_distance_selection",
    # stimulation utilities for the network
    "stimulate", "voltage_initialization",
    # logging utilities & setups
    "LOGGER_NAME",
    # plotting utils
    "plot"
]
