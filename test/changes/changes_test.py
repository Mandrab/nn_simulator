import json
import networkx as nx
import numpy as np

from itertools import product
from nn_simulator import *
from nn_simulator.logger import *
from nn_simulator.model.device.factory import largest_connected_component
from test.model.device.utils import equals


################################################################################
# TEST FUNCTIONS

def import_graph(file_name):
    with open(file_name, 'r') as file:
        text = json.load(file)
        graph = nx.node_link_graph(text)
    return graph


################################################################################
# NETWORK SETUP


def test_data_equality():
    wires_dict = generate_network_data(default)

    with open('test/changes/wires.dat', 'r') as file:
        expected = json.load(file)

    assert sorted(wires_dict.keys()) == sorted(expected.keys())
    for k in sorted(wires_dict.keys()):
        value_a, value_b = wires_dict[k], expected[k]
        if isinstance(value_b, list):
            np.allclose(value_a, np.asarray(value_b))
        else:
            assert value_a == value_b


def test_original_behaviour():
    """Test that the modified simulator behaves as the original one"""

    # generate the network
    wires_dict = generate_network_data(default)
    network = nanowire_network(wires_dict, default.Y_min)

    # get the deleted nodes mask
    _, mask = largest_connected_component(wires_dict['adj_matrix'])

    # calculate the new index of original source (i.e. 274)
    source = 274 - sum(mask[:274])

    # set ground node in the network
    network.device_grounds += 1

    expected = import_graph('test/changes/simplification.dat')
    expected = nx2nn(expected)
    expected.device_grounds += 1

    equals(network, expected)
    logging.info('TEST: simplified graphs are equals')

    ############################################################################
    # ELECTRICAL STIMULATION

    logging.debug('Electrical stimulation of the network')

    pulse_duration, reads = 10, 80
    v, delta_t = 10.0, 0.05

    # generate vin stimulation for each input
    stimulation = [v] * pulse_duration + [0.01] * reads
    stimulation = list(product([source], stimulation))

    # growth of the conductive path
    logging.debug('Growth of the conductive path')

    # first stimulation comparison
    stimulate(network, default, delta_t, dict([stimulation[0]]))

    expected = import_graph('test/changes/stimulation_1.dat')
    expected = nx2nn(expected)
    expected.device_grounds += 1

    equals(network, expected)

    # growth over time
    for signal in stimulation[1:]:
        stimulate(network, default, delta_t, dict([signal]))

    expected = import_graph('test/changes/stimulation.dat')
    expected = nx2nn(expected)
    expected.device_grounds += 1

    equals(network, expected)

    logging.info('TEST: stimulated graphs are equals')
