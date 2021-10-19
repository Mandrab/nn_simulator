# -*- coding: utf-8 -*-

# standard lib
import logging

# project files
from model import NetworkUtils
from model.NetworkStimulator import NetworkStimulator
from model.inspect import print_info, inspect, information_centrality
from view import plot

logging.basicConfig(level = logging.DEBUG, format = '[%(asctime)s %(levelname)s]\t %(message)s')
