#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 27 08:06:18 2019

@author: Gianluca
"""
import math
import random
from networkx import grid_graph

import networkx as nx


# GRAPH DEFINITION
def __define_grid_graph(xdim, ydim, config=lambda _: _):
    graph = config(grid_graph(dim=[xdim, ydim]))

    return nx.convert_node_labels_to_integers(
        graph,
        first_label=0,
        ordering='default',
        label_attribute='pos'
    )


define_grid_graph = __define_grid_graph


# GRAPH DEFINITION_2  (with random diagonals)
def define_grid_graph_2(xdim, ydim):
    def init(graph):
        for x in range(xdim - 1):
            for y in range(ydim - 1):
                k = random.randint(0, 1)
                if k == 0:
                    graph.add_edge((x, y), (x + 1, y + 1))
                else:
                    graph.add_edge((x + 1, y), (x, y + 1))

    return __define_grid_graph(xdim, ydim, init)


# GRAPH INITIALIZATION
def initialize_graph_attributes(G, Yin):
    # add the initial conductance
    for u, v in G.edges():
        # assign initial admittance to all edges
        G[u][v]['Y'] = Yin

        # assign initial high resistance state in all junctions
        G[u][v]['R'] = 1 / G[u][v]['Y']

        G[u][v]['deltaV'] = 0
        G[u][v]['g'] = 0

    # initialize
    for n in G.nodes():
        G.nodes[n]['pad'] = False
        G.nodes[n]['source_node'] = False
        G.nodes[n]['ground_node'] = False

    return G


###############################################################################

# CALCULATE NETWORK RESISTANCE
def calculate_network_resistance(H, source_node):
    return H.nodes[source_node]['V'] / calculate_source_current(H, source_node)


# CALCULATE V SOURCE
def calculate_source_voltage(H, source_node):
    return H.nodes[source_node]['V']


# CALCULATE I SOURCE
def calculate_source_current(H, source_node):
    source_current = 0
    for u, v in H.edges(source_node):
        source_current += H[u][v]['I']

    return source_current


###############################################################################


# UPDATE EDGE WEIGHT (Miranda's model)
def update_edge_weights(device, datasheet, delta_t):
    graph = device.connected_nodes[0]
    for u, v in graph.edges():
        edge = graph[u][v]

        edge['deltaV'] = abs(graph.nodes[u]['V'] - graph.nodes[v]['V'])
        edge['kp'] = datasheet.kp0 * math.exp(datasheet.eta_p * edge['deltaV'])
        edge['kd'] = datasheet.kd0 * math.exp(-datasheet.eta_d * edge['deltaV'])
        edge['g'] = (
                edge['kp'] / (edge['kp'] + edge['kd'])
            ) * (
                1 - (
                    1 - (1 + (edge['kd'] / edge['kp']) * edge['g'])
                ) * math.exp(
                    -(edge['kp'] + edge['kd']) * delta_t
                )
            )
        edge['Y'] = datasheet.Y_min * (1 - edge['g']) + datasheet.Y_max * edge['g']
        edge['R'] = 1 / edge['Y']


# FIND CONNECTED COMPONENTS
def connected_component_subgraphs(G):
    for c in nx.connected_components(G):
        yield G.subgraph(c)
