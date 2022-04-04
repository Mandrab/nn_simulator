#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plotting utils.

@author: Gianluca Milano
@author: Paolo Baldini
"""
import matplotlib.pyplot as plt
import networkx as nx

from functools import cache
from matplotlib.lines import Line2D
from networkx import Graph
from typing import Set, Any


def draw_wires(ax, wires_dict):
    """
    Draw wires on a given set of axes.
    
    Wires outside the domain are light gray dashed lines. 
    Wires inside the domain are light gray solid lines. 
    The centre of the wires is marked with a red 'o' marker. 
    
    ax -- matplotlib axes to draw needle symbol
    wires_dict  -- dictionary output from generate_distribution
    """

    # Make local variables
    xa, ya = wires_dict['xa'], wires_dict['ya']
    xb, yb = wires_dict['xb'], wires_dict['yb']
    xc, yc = wires_dict['xc'], wires_dict['yc']

    for wire in range(wires_dict['number_of_wires']):
        a, b = [xa[wire], xb[wire]], [ya[wire], yb[wire]]
        ax.add_line(Line2D(a, b, color=(0.42, 0.42, 0.42)))

        a, b = [xc[wire]], [yc[wire]]
        ax.add_line(Line2D(a, b, color='r', marker='o', alpha=0.77, ms=2))

    return ax


def draw_junctions(ax, wires_dict):
    """Draw the circles at the junctions"""

    for junction in range(wires_dict['number_of_junctions']):
        a, b = [wires_dict['xi'][junction]], [wires_dict['yi'][junction]],
        ax.add_line(Line2D(a, b, color='b', marker='o', alpha=0.77, ms=1.5))

    return ax


def draw(graph: Graph, opt: dict, color, size: int = 20, label: bool = False):
    opt = dict(node_color=color, node_size=size, with_labels=label) | opt
    nx.draw_networkx(graph, nx.get_node_attributes(graph, 'pos'), **opt)


def line_graph(ax, x, *data):
    plt.cla()

    colors = iter(['b', 'g', 'r', 'c', 'm', 'y'] * len(data))
    for data, color in zip(data, colors):
        ax.plot(x, data, color=color)
        ax.tick_params(axis='y', labelcolor=color)

        # instantiate a second axes that shares the same x-axis
        ax = ax.twinx()


def draw_network(
        graph: Graph,
        sources: Set[int], grounds: Set[int], loads: Set[int],
        edge_min: float = None, edge_max: float = None,
        normal_sizes: Any = 20,
        normal_node_colors: Any = '#1f78b4', normal_edge_colors: Any = 'k',
        **others
):
    nx.draw_networkx(
        graph,
        nodes_positions(graph),
        **dicts(
            others['default'] if 'default' in others else {},
            node_size=normal_sizes,
            node_color=normal_node_colors, edge_color=normal_edge_colors,
            cmap=plt.cm.get_cmap('cool'), edge_cmap=plt.cm.get_cmap('Reds'),
            width=2,
            edge_vmin=edge_min, edge_vmax=edge_max,
            arrows=False,
            with_labels=False,
            font_size=6
        )
    )

    for data, color in zip([sources, grounds, loads], ['r', 'k', 'y']):
        highlight(graph, data, color, others.get('others', {}))


def highlight(graph: Graph, nodes: Set[int], color: str, others):
    config = dict(nodelist=nodes, node_size=300, node_color=color, alpha=0.5)
    nx.draw_networkx_nodes(graph, nodes_positions(graph), **(config | others))


@cache
def nodes_positions(graph: Graph): return nx.get_node_attributes(graph, 'pos')


@cache
def list_connected_components(graph: Graph):
    """Return sorted list of connected components"""
    return sorted(nx.connected_components(graph), key=len, reverse=True)


def dicts(new, **default): return default | new
