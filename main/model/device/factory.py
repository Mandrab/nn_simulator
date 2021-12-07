import logging
import networkx as nx

from main.model import wires
from networkx import Graph
from . import Datasheet
from typing import Tuple
from .utils import largest_component


def generate_network(datasheet: Datasheet) -> dict:
    """Generate the network according to the datasheet specifications"""

    logging.info('Generating network')

    # generate the network
    wires_dict = wires.generate_wires_distribution(
        number_of_wires=datasheet.wires_count,
        wire_av_length=datasheet.mean_length,
        wire_dispersion=datasheet.std_length,
        general_normal_shape=10,
        centroid_dispersion=datasheet.centroid_dispersion,
        seed=datasheet.seed,
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

    return graph


def generate_graph(datasheet: Datasheet) -> Graph:
    """Get the graph from a datasheet specification"""

    return get_graph(generate_network(datasheet))


def minimum_viable_network(datasheet: Datasheet) -> Tuple[Graph, dict]:
    """
    Produce the network specified by the datasheet.
    To improve speed, reduce the network to the largest connected component.
    For only 1 ground that is ok, but for more it may limit the potential of the
    network: disjoint components may result in better performance when the
    output are not correlated (todo that is just an hypothesis).
    """

    # create a device that is represented by the given datasheet
    wires_dict = generate_network(datasheet)

    # calculate the minimum network and return it with its original wires-dict
    return largest_component(get_graph(wires_dict), relabel=True), wires_dict
