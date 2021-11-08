import logging
import networkx as nx

from networkx import Graph

from model import wires
from model.device.datasheet.Datasheet import Datasheet


def generate_network(datasheet: Datasheet) -> dict:
    """Generate the network according to the datasheet specifications"""

    logging.info('Generating network')

    # generate the network
    wires_dict = wires.generate_wires_distribution(
        number_of_wires=datasheet.wires_count,
        wire_av_length=datasheet.mean_length,
        wire_dispersion=datasheet.std_length,
        gennorm_shape=10,
        centroid_dispersion=datasheet.centroid_dispersion,
        this_seed=datasheet.seed,
        Lx=datasheet.Lx,
        Ly=datasheet.Ly
    )

    # get junctions list and their positions
    wires.detect_junctions(wires_dict)

    # generate graph object and adjacency matrix
    wires.generate_graph(wires_dict)

    return wires_dict


def get_graph(wires_dict: dict) -> Graph:
    """Generate graph from specifications"""

    logging.debug('Extracting graph from network')

    adj_matrix = wires_dict['adj_matrix']

    # complete graph with also unconnected nodes
    graph = nx.from_numpy_matrix(adj_matrix)

    xpos = [x for x in wires_dict['xc']]
    ypos = [y for y in wires_dict['yc']]

    xjpos = [x for x in wires_dict['xi']]
    yjpos = [y for y in wires_dict['yi']]

    # add node and junction positions as graph attributes (from dictionary)
    for n in graph.nodes():
        graph.nodes[n]['pos'] = (xpos[n], ypos[n])

    n = 0
    for u, v in graph.edges():
        graph[u][v]['jx_pos'] = (xjpos[n], yjpos[n])
        n = n + 1

    '''
    #list of wire lengths
    wire_lengths = xpos = [x for x in wires_dict['wire_lengths']]
    '''

    return graph


def generate_graph(datasheet: Datasheet) -> Graph:
    """Get the graph from a datasheet specification"""

    return get_graph(generate_network(datasheet))
