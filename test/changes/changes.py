import json
import networkx as nx

from collections.abc import Iterable
from main import *


################################################################################
# TEST FUNCTIONS

def import_graph(file_name):
    with open(file_name, 'r') as file:
        text = json.load(file)
        g = nx.node_link_graph(text)
    return g


def are_equal(g1, g2):
    default_precision = 1e-4
    g_precision = 1e-2
    r_precision = 20

    def equals(v1, v2, precision):

        if isinstance(v1, Iterable):
            iterable = iter(v2)
            for e1 in value:
                e2 = next(iterable)
                if abs(e1 - e2) > precision:
                    logging.error(f'For {key}: expected {v1:.4f}, got {v2:.4f}')
        elif abs(v1 - v2) > precision:
            logging.error(f'For {key}: expected {v1:.4f}, got {v2:.4f}')

    for node in g1.nodes():
        for key, value in g1.nodes[node].items():
            other = g2.nodes[node][key]
            equals(value, other, default_precision)

    for source, destination in g1.edges():
        for key, value in g1[source][destination].items():
            other = g2[source][destination][key]
            if key == 'R':
                equals(value, other, r_precision)
            else:
                equals(value, other, g_precision)


################################################################################
# NETWORK SETUP

def test_original_behaviour():
    """Test that the modified simulator behaves as the original one"""

    wires_dict = generate_network(default)
    graph = get_graph(wires_dict)

    expected = import_graph('test/creation.dat')
    are_equal(graph, expected)
    logging.info('TEST: created graphs are equals')

    grounds = {358}
    sources = {273}

    removed_nodes = [
        n for n in graph.nodes()
        if not nx.has_path(graph, n, next(iter(grounds)))
    ]
    graph.remove_nodes_from(removed_nodes)
    mapping = dict(zip(graph, range(graph.number_of_nodes())))
    graph = nx.relabel_nodes(graph, mapping)
    grounds = {mapping[g] for g in grounds}
    sources = {mapping[s] for s in sources}

    expected = import_graph('test/simplification.dat')
    are_equal(graph, expected)
    logging.info('TEST: simplified graphs are equals')

    ############################################################################
    # ELECTRICAL STIMULATION

    logging.info('Electrical stimulation of the network')

    steps = 90              # simulation duration
    pulse_duration = 10     # duration of a stimulation pulse (in steps)
    reads = 80              # reads at output
    pulse_count = 1         # number of stimulation pulses
    delta_t = 0.05          # virtual time delta

    v = 10.0                # pulse amplitude of stimulation

    # generate vin stimulation for each input
    stimulations = [v] * pulse_duration * pulse_count + [0.01] * reads
    stimulations = [
        [(source, stimulations[i]) for source in sources]
        for i in range(steps)
    ]

    # growth of the conductive path
    logging.info('Growth of the conductive path')

    # initialize network
    initialize_graph_attributes(graph, sources, grounds, default.Y_min)
    voltage_initialization(graph, sources, grounds)

    expected = import_graph('test/initialization.dat')
    are_equal(graph, expected)
    logging.info('TEST: initialized graphs are equals')

    # growth over time
    for i in range(steps):
        stimulate(graph, default, delta_t, stimulations[i], [], grounds)

    expected = import_graph('test/stimulation.dat')
    are_equal(graph, expected)
    logging.info('TEST: stimulated graphs are equals')
