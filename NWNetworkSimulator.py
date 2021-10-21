# -*- coding: utf-8 -*-

# standard lib
import logging

# project files
from model import NetworkUtils
from model.device.default import default
from model.inspect import print_info, inspect, information_centrality
from model.NetworkStimulator import NetworkStimulator

# from view.view import plot_all

logging.basicConfig(level=logging.INFO, format='[%(asctime)s %(levelname)s]\t %(message)s')
