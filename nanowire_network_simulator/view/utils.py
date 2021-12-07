#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 27 15:09:29 2019

@author: Gianluca
"""

import matplotlib.pyplot as plt
import networkx as nx

from matplotlib.lines import Line2D


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

    for this_wire in range(wires_dict['number_of_wires']):
        lines = [
            Line2D(
                [xa[this_wire], xb[this_wire]],
                [ya[this_wire], yb[this_wire]],
                color=(0.42, 0.42, 0.42)
            ),
            Line2D(
                [xc[this_wire]],
                [yc[this_wire]],
                color='r', marker='o', alpha=0.77,
                ms=2
            )
        ]

        '''
        if wires_dict['outside'][this_wire]:
            lines = [
                Line2D(
                    [xa[this_wire], xb[this_wire]],
                    [ya[this_wire], yb[this_wire]],
                    color='k', ls='--', alpha=0.2
                ),
                # Line2D(
                #     [xc[this_wire]], [yc[this_wire]],
                #     color='k', marker='o', alpha=0.1,
                #     ms=4
                # )
            ] 
        else:   
            lines = [
                Line2D(
                    [xa[this_wire], xb[this_wire]],
                    [ya[this_wire], yb[this_wire]],
                    color=(0.42, 0.42, 0.42)
                ),
                Line2D(
                    [xc[this_wire]],
                    [yc[this_wire]],
                    color='r', marker='o', alpha=0.77,
                    ms=2,
                )
            ]
        '''
        for line in lines:
            ax.add_line(line)

    return ax


def draw_junctions(ax, wires_dict):
    """Draw the circles at the junctions"""

    xi, yi = wires_dict['xi'], wires_dict['yi']

    for this_junction in range(wires_dict['number_of_junctions']):
        lines = [
            Line2D(
                [xi[this_junction]],
                [yi[this_junction]],
                color='b', marker='o', alpha=0.77,
                ms=1.5,
            )
        ]
        for line in lines:
            ax.add_line(line)

    return ax


def plot_0(graph):
    pos = nx.get_node_attributes(graph, 'pos')
    plt.figure()

    node_colors = [[] for _ in range(0, graph.number_of_nodes())]

    # for n in H.nodes():
    #     node_colors[n] = 'r'
    #     if H.nodes[n]['pad'] == True:
    #         node_colors[n] = 'y'
    #     if H.nodes[n]['source_node'] == True:
    #         node_colors[n] = 'm'
    #     if H.nodes[n]['ground_node'] == True:
    #         node_colors[n] = 'k'

    nx.draw_networkx(
        graph, pos,
        node_color=node_colors, node_size=60,
        with_labels=True
    )
    # nx.draw_networkx_edges(
    #     graph, pos,
    #     edgelist=filament_edges, edge_color='r', width=10
    # )


def plot_1(graph):
    """Graph with node numbers and edge conductance"""
    pos = nx.get_node_attributes(graph, 'pos')
    conductance = nx.get_edge_attributes(graph, 'Y')

    filament_edges = [
        (u, v) for u, v, e in graph.edges(data=True) if e['Filament'] == 1
    ]

    plt.figure()

    nx.draw_networkx(graph, pos)
    nx.draw_networkx_edge_labels(
        graph, pos,
        edge_labels=conductance, font_size=6
    )
    nx.draw_networkx_edges(
        graph, pos,
        edgelist=filament_edges, edge_color='r', width=10
    )


def plot_2(graph):
    """Graph with voltage node labels and edge conductance"""
    pos = nx.get_node_attributes(graph, 'pos')
    conductance = nx.get_edge_attributes(graph, 'Y')
    for n in graph.nodes():  # rounded Voltage
        graph.node[n]['v_rounded'] = round(graph.node[n]['V'], 2)

    v_label = nx.get_node_attributes(graph, 'v_rounded')

    node_colors_2 = [[] for _ in range(0, graph.number_of_nodes())]

    filament_edges = [(u, v) for u, v, e in graph.edges(data=True) if
                      e['Filament'] == 1]  # add color to nodes

    # source_node = [x for x,y in H.nodes(data = True) if y['source_node']]

    for n in graph.nodes():
        node_colors_2[n] = 'r'
        if graph.nodes[n]['source_node']:
            node_colors_2[n] = 'g'
        if n == 0:
            node_colors_2[n] = 'y'

    plt.figure()

    nx.draw_networkx(
        graph, pos,
        labels=v_label, font_size=8,
        node_color=node_colors_2
    )
    nx.draw_networkx_edge_labels(
        graph, pos,
        edge_labels=conductance,
        font_size=6
    )
    nx.draw_networkx_edges(
        graph, pos,
        edgelist=filament_edges, edge_color='r', width=10
    )


def plot_3(graph):
    """Graph with voltage node labels and current"""
    pos = nx.get_node_attributes(graph, 'pos')
    for n in graph.nodes():  # rounded Voltage
        graph.node[n]['v_rounded'] = round(graph.node[n]['V'], 2)

    v_label = nx.get_node_attributes(graph, 'v_rounded')
    i_label = nx.get_edge_attributes(graph, 'i_rounded')

    node_colors_2 = [
        [] for _ in range(0, graph.number_of_nodes())
    ]  # add color to nodes

    '''
    source_node = [x for x,y in graph.nodes(data = True) if y['source_node']]
    '''
    for n in graph.nodes():
        node_colors_2[n] = 'r'
        if graph.nodes[n]['source_node']:
            node_colors_2[n] = 'g'
        if n == 0:
            node_colors_2[n] = 'y'

    plt.figure()

    nx.draw_networkx(
        graph, pos,
        labels=v_label, font_size=8,
        node_color=node_colors_2
    )
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=i_label)


def plot_4(graph):
    """Graph with voltage node labels and current and colors"""
    pos = nx.get_node_attributes(graph, 'pos')

    for n in graph.nodes():  # rounded Voltage
        graph.node[n]['v_rounded'] = round(graph.node[n]['V'], 2)

    v_label = nx.get_node_attributes(graph, 'v_rounded')
    i_label = nx.get_edge_attributes(graph, 'i_rounded')

    # plot with labels
    plt.figure()
    nx.draw_networkx(
        graph, pos,
        node_color=[graph.nodes[n]['V'] for n in graph.nodes()],
        cmap=plt.cm.Blues,
        edge_color=[graph[u][v]['I'] for u, v in graph.edges()],
        edge_labels=i_label, width=4, edge_cmap=plt.cm.Reds,
        with_labels=True, labels=v_label, font_size=6
    )

    nx.draw_networkx_edge_labels(graph, pos, edge_labels=i_label, font_size=6)


def plot_5(graph):
    """As plot 4 but without node and edge labels"""
    plt.figure()
    nx.draw_networkx(
        graph, nx.get_node_attributes(graph, 'pos'),
        node_size=60, node_color=[graph.nodes[n]['V'] for n in graph.nodes()],
        cmap=plt.cm.Blues,
        edge_color=[graph[u][v]['I'] for u, v in graph.edges()], width=4,
        edge_cmap=plt.cm.Reds,
        with_labels=False, font_size=6
    )
