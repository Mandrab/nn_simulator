#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
import networkx as nx

from networkx import grid_graph, Graph
from typing import Set


def largest_component(graph: Graph, relabel: bool = False) -> Graph:
    """
    Get the graph of largest connected component of the network.
    If required, relabel the nodes with incremental indexes.
    The original graph is not modified.
    """

    # does not override the original graph
    graph = graph.copy()

    # remove nodes that are not in the largest connected network
    graph.remove_nodes_from(
        {*graph.nodes} - {*max(nx.connected_components(graph), key=len)}
    )

    # relabel the node with incremental indexes
    if relabel:
        mapping = dict(zip(graph, range(graph.number_of_nodes())))
        graph = nx.relabel_nodes(graph, mapping)

    return graph


def define_grid_graph(x_size: int, y_size: int, config=lambda _: _) -> Graph:
    """Define a graph"""

    graph = config(grid_graph(dim=[x_size, y_size]))

    return nx.convert_node_labels_to_integers(
        graph,
        first_label=0,
        ordering='default',
        label_attribute='pos'
    )


def define_grid_graph_2(x_size: int, y_size: int) -> Graph:
    """Graph definition with random diagonals"""

    def init(graph):
        for x in range(x_size - 1):
            for y in range(y_size - 1):
                k = random.randint(0, 1)
                if k == 0:
                    graph.add_edge((x, y), (x + 1, y + 1))
                else:
                    graph.add_edge((x + 1, y), (x, y + 1))

    return define_grid_graph(x_size, y_size, init)


def initialize_graph_attributes(
        graph: Graph,
        sources: Set[int],
        grounds: Set[int],
        y_in: float
):
    """Initialize graph parameters"""

    # add the initial conductance
    for u, v in graph.edges():
        # assign initial admittance to all edges
        graph[u][v]['Y'] = y_in

        # assign initial high resistance state in all junctions
        graph[u][v]['R'] = 1 / graph[u][v]['Y']

        graph[u][v]['deltaV'] = 0
        graph[u][v]['g'] = 0

    # initialize todo probably useless
    for n in graph.nodes():
        graph.nodes[n]['pad'] = False
        graph.nodes[n]['source_node'] = n in sources
        graph.nodes[n]['ground_node'] = n in grounds
