import logging
import networkx as nx

from functools import cached_property
from model.device.factory import get_graph, generate_network
from model.functions import initialize_graph_attributes

PATH_ERROR = 'A source is not connected to any ground!'


class Device:

    def __init__(self, datasheet, source_nodes, ground_nodes):
        # device specifications
        self.__datasheet = datasheet

        # source and ground nodes positions
        self.source_nodes = source_nodes
        self.ground_nodes = ground_nodes

    @cached_property
    def graph(self):
        return get_graph(self.network)

    @cached_property
    def network(self):
        return generate_network(self.__datasheet)

    @cached_property
    def connected_nodes(self):
        return connected_nodes(self, self.__datasheet)


def connected_nodes(device, datasheet):
    # select connected graph (between source and ground node)
    logging.debug('Get nodes connected to source and ground')

    # return true if the node is connected to at least one ground, false otherwise
    def grounded(node):
        return next(
            (True for ground in device.ground_nodes
             if nx.has_path(device.graph, node, ground)),
            False  # node is not connected to any ground. avoid exception
        )

    # remove nodes not connected to any ground
    removed_nodes = [n for n in device.graph.nodes() if not grounded(n)]

    # check that not source node is removed. i.e. not connected to any ground
    assert not any(n in device.source_nodes for n in removed_nodes), PATH_ERROR

    M = device.graph.copy()
    M.remove_nodes_from(removed_nodes)

    # relabel node names (for mod_voltage node analysis)
    mapping = dict(zip(M, range(M.number_of_nodes())))
    M = nx.relabel_nodes(M, mapping)

    M = initialize_graph_attributes(M, datasheet.Y_min)

    # set source node label
    for source in device.source_nodes:
        M.nodes[mapping[source]]['source_node'] = True

    # set ground node label
    for ground in device.ground_nodes:
        M.nodes[mapping[ground]]['ground_node'] = True

    return M, mapping
