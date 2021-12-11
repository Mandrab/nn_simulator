# -*- coding: utf-8 -*-
import collections
import logging
import matplotlib.pyplot as plt
import networkx as nx

from functools import cache
from matplotlib.animation import FuncAnimation, ImageMagickWriter
from ..model.analysis.evolution import Evolution
from ..model.device.utils import largest_component
from networkx import Graph
from .utils import draw_wires, draw_junctions
from typing import Set, Any, Callable

logging.getLogger('matplotlib.font_manager').disabled = True
logging.getLogger('matplotlib.colorbar').disabled = True


def plot(data: Evolution, filler: Callable[[Any, Any, Evolution], None]):
    """Standard plotting setup"""
    fig = plt.figure(figsize=(10, 10))
    ax = fig.subplots()

    # add some space around the unit square
    ax.axis([
        -.1 * data.datasheet.Lx, 1.1 * data.datasheet.Lx,
        -.1 * data.datasheet.Ly, 1.1 * data.datasheet.Ly
    ])

    # set axes labels and grid
    ax.set(xlabel=r'x ($\mu$m)', ylabel=r'y ($\mu$m)')
    ax.ticklabel_format(style='plain', scilimits=(0, 0))
    ax.grid()

    # add data to plot
    filler(fig, ax, data)

    plt.show()


def adj_matrix(_0, _1, plot_data: Evolution, **_2):
    """Plot adjacency matrix"""
    plt.imshow(plot_data.wires_dict['adj_matrix'], cmap='binary')
    plt.colorbar()


def network(_0, ax, plot_data: Evolution, **_1):
    """Plot nano-wires distribution from wires_dict (network)"""
    ax.set(title='Nano-wires distribution')
    draw_wires(ax, plot_data.wires_dict)
    draw_junctions(ax, plot_data.wires_dict)


def graph(_, ax, plot_data: Evolution, **others):
    """Plot nano-wires distribution from graph"""
    ax.set(title='Nano-wires distribution graph')
    nx.draw_networkx(
        plot_data.graph,
        nx.get_node_attributes(plot_data.graph, 'pos'),
        **__dicts(others, node_color='r', node_size=20, with_labels=True)
    )


def kamada_kawai_graph(_, ax, plot_data: Evolution, **others):
    """Plot nano-wires distribution from graph (kamada-style)"""
    plt.cla()  # override default axis config

    ax.set(title='Nano-wires distribution (Kamada-Kawai)')
    nx.draw_kamada_kawai(
        plot_data.graph,
        **__dicts(others, node_color='r', node_size=20, with_labels=False)
    )


def degree_of_nodes(_0, ax, plot_data: Evolution, **_1):
    """Print a diagram representing, for each degree, its quantity"""
    plt.cla()  # override default axis config

    # print "Degree sequence", degree_sequence todo
    degree_count = collections.Counter(
        sorted([d for _, d in plot_data.graph.degree()], reverse=True)
    ).items()
    deg, cnt = zip(*degree_count)

    plt.bar(deg, cnt, width=0.8, color='b', align='center')

    ax.set(
        title="Degree Histogram",
        ylabel='Count', xlabel='Degree',
        xticks=[d for d in deg], xticklabels=deg
    )


def highlight_connected_components(_, ax, plot_data: Evolution, **others):
    """Print connected components in the network (different colors for each)"""
    ax.set(title='Connected components')

    components = __list_connected_components(plot_data.graph)

    n = round(len(components) / 5) + 1
    colors = ['r'] + ['g', 'b', 'c', 'm', 'y'] * n

    # set node-color for print (different between components)
    for index, component in enumerate(components):

        # get nodes of the component
        a = [x for x in component]

        # color differently isolated nodes
        if len(a) == 1:
            plot_data.graph.nodes[a[0]]['component_color'] = 'k'
            continue

        for node in a:
            plot_data.graph.nodes[node]['component_color'] = colors[index]

    nx.draw_networkx(
        plot_data.graph,
        nx.get_node_attributes(plot_data.graph, 'pos'),
        **__dicts(
            others,
            node_color=[plot_data.graph.nodes[u]['component_color'] for u in
                        plot_data.graph.nodes()],
            node_size=20,
            with_labels=False
        )
    )


def largest_connected_component(_, ax, plot_data: Evolution, **others):
    """Plot only the largest connected component"""
    ax.set(title='Nanowires distribution graph')
    nx.draw_networkx(
        largest_component(plot_data.graph), __nodes_positions(plot_data.graph),
        **__dicts(others, node_color='r', node_size=20, with_labels=True)
    )


def network_7(_, ax, plot_data: Evolution, **others):
    """Print connected components in the network (different colors for each)"""
    # todo difference from 'highlight_connected_components'?
    ax.set(title='Connected components')

    components = __list_connected_components(plot_data.graph)

    n = round(len(components) / 5) + 1
    colors = ['b'] + ['lightgray'] * n * 5

    # set node-color for print (different between components)
    for index, component in enumerate(components):

        # get nodes of the component
        a = [x for x in component]

        # color differently isolated nodes
        if len(a) == 1:
            plot_data.graph.nodes[a[0]]['component_color'] = 'lightgray'
            continue

        for node in a:
            plot_data.graph.nodes[node]['component_color'] = colors[index]

    nx.draw_networkx(
        plot_data.graph,
        __nodes_positions(plot_data.graph),
        **__dicts(
            others['default'] if 'default' in others else {},
            node_color=[
                plot_data.graph.nodes[node]['component_color']
                for node in plot_data.graph.nodes()
            ],
            node_size=20,
            with_labels=False
        )
    )

    nx.draw_networkx_nodes(
        plot_data.graph,
        __nodes_positions(plot_data.graph),
        **__dicts(
            others['inputs'] if 'inputs' in others else {},
            nodelist=[*map(lambda v: v[0], plot_data.inputs)],
            # todo makes no sense if input change in time
            node_color='r',
            node_size=300,
            alpha=0.5
        )
    )
    nx.draw_networkx_nodes(
        plot_data.graph,
        __nodes_positions(plot_data.graph),
        **__dicts(
            others['loads'] if 'loads' in others else {},
            nodelist=plot_data.grounds | {n for n, _ in plot_data.loads},
            node_color='k',
            node_size=300,
            alpha=0.5
        )
    )


def conductance(fig, ax1, plot_data: Evolution, **_1):
    """Display the max conductivity of a path in the network for each state"""
    plt.cla()  # override default axis config

    # calculate network minimum resistance
    resistances = [
        min([
            (source, nx.resistance_distance(
                graph,
                source,
                [*plot_data.grounds | {n for n, _ in plot_data.loads}][0],  # todo
                weight='Y',
                invert_weight=False
            )) for source, _ in inputs
        ]) for graph, inputs in plot_data.network_instances
    ]
    sources_voltages = [
        next(v for s_, v in plot_data.network_instances[i][1] if s_ == s)
        for i, (s, r) in enumerate(resistances)
    ]
    conductances = [1 / v for _, v in resistances]

    color = 'tab:red'
    ax1.set_xlabel('time (s)')
    ax1.set_ylabel('Input Voltage (V)', color=color)

    ax1.plot(plot_data.update_times, sources_voltages, color=color)
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

    color = 'tab:blue'
    ax2.set_ylabel('Conductance (S)',
                   color=color)  # we already handled the x-label with ax1

    ax2.plot(plot_data.update_times, conductances, color=color)
    ax2.tick_params(axis='y', labelcolor=color)

    fig.tight_layout()  # otherwise the right y-label is slightly clipped

    plt.title('Network conductance')


def voltage_distribution_map(_, ax, plot_data: Evolution, **others):
    """Plot the voltage distribution (intensity) of the initial graph"""  # todo
    ax.set(title='Nano-wires distribution graph')
    graph = next(iter(plot_data.currents_graphs())).copy()
    __draw_network(
        graph,
        plot_data.sources, plot_data.grounds, {n for n, _ in plot_data.loads},
        plot_data.datasheet.Y_min, plot_data.datasheet.Y_max,
        normal_node_colors=[graph.nodes[n]['V'] for n in graph.nodes()],
        **__dicts(others, default=dict(ax=ax), others=dict(ax=ax))
    )


def conductance_map(_, ax, plot_data: Evolution, **others):
    """Plot the conductance distribution of the final graph"""  # todo
    ax.set(title='Nano-wires distribution graph')
    graph = next(iter(plot_data.currents_graphs(reverse=True))).copy()
    __draw_network(
        graph,
        plot_data.sources, plot_data.grounds, {n for n, _ in plot_data.loads},
        plot_data.datasheet.Y_min, plot_data.datasheet.Y_max, 20,
        [graph.nodes[n]['V'] for n in graph.nodes()],
        [graph[u][v]['Y'] for u, v in graph.edges()],
        **__dicts(others, default=dict(ax=ax), others=dict(ax=ax))
    )


def information_centrality_map(_, ax, plot_data: Evolution, **others):
    """Plot the information centrality of the final graph"""  # todo
    ax.set(title='Nano-wires distribution graph')

    # scaling information centrality to node sizes
    information_centralities = [*plot_data.information_centrality()]
    L = information_centralities[-1]

    min_centrality = min([min(element) for element in information_centralities])
    max_centrality = max([max(element) for element in information_centralities])

    min_node_size = 0.0001
    max_node_size = 60

    m = (max_node_size - min_node_size) / (max_centrality - min_centrality)
    b = max_node_size - (m * max_centrality)

    centrality_normalized = [(m * v) + b for v in information_centralities[-1]]

    __draw_network(
        plot_data.graph,
        plot_data.sources, plot_data.grounds, {n for n, _ in plot_data.loads},
        plot_data.datasheet.Y_min, plot_data.datasheet.Y_max,
        centrality_normalized,
        [L.nodes[n]['information_centrality'] for n in L.nodes],
        [L[u][v]['Y'] for u, v in L.edges()],
        **__dicts(others, default=dict(ax=ax), others=dict(ax=ax))
    )


def animation(fig, ax, plot_data: Evolution, **others):
    """Plot animated conductance evolution"""
    frames = len(plot_data.network_instances) - 1

    hs = [*plot_data.currents_graphs()]

    def update(i):
        plt.cla()

        nx.draw_networkx(
            hs[i],
            __nodes_positions(hs[i]),
            # NODES
            node_size=60,
            node_color=[hs[i].nodes[n]['V'] for n in hs[i].nodes()],
            cmap=plt.cm.get_cmap('Blues'),
            vmin=-5, vmax=10,
            # EDGES
            width=4,
            edge_color=[hs[i][u][v]['Y'] for u, v in hs[i].edges()],
            edge_cmap=plt.cm.get_cmap('Reds'),
            edge_vmin=plot_data.datasheet.Y_min,
            edge_vmax=plot_data.datasheet.Y_max,
            with_labels=False,  # set TRUE to see node numbers
            font_size=6
        )
        ax.set(title="t = {}".format(round(plot_data.update_times[i], 1)))

    # animation
    FuncAnimation(
        fig, update,
        **__dicts(others, frames=frames, interval=500, blit=False, repeat=True)
    ).save('animation_1.gif', writer='imagemagick')


def animation_kamada_kawai(fig, ax, plot_data: Evolution, **others):
    """Plot animated conductance evolution in kamada kawai style"""
    frames = len(plot_data.network_instances) - 1

    hs = [*plot_data.currents_graphs()]
    t_list = [i * plot_data.delta_time for i in range(frames)]

    def update(i):
        plt.cla()

        nx.draw_kamada_kawai(
            hs[i],
            # NODES
            node_size=60,
            node_color=[hs[i].nodes[n]['V'] for n in hs[i].nodes()],
            cmap=plt.cm.get_cmap('Blues'),
            vmin=-5, vmax=10,
            # EDGES
            width=4,
            edge_color=[hs[i][u][v]['Y'] for u, v in hs[i].edges()],
            edge_cmap=plt.cm.get_cmap('Reds'),
            edge_vmin=plot_data.datasheet.Y_min,
            edge_vmax=plot_data.datasheet.Y_max,
            with_labels=False,  # Set TRUE to see node numbers
            font_size=6
        )

        ax.set_title("t = {}".format(round(t_list[i], 1)))

    FuncAnimation(
        fig, update,
        **__dicts(others, frames=frames, interval=500, blit=False, repeat=True)
    ).save('animation_2.gif', writer=ImageMagickWriter(fps=2))


def outputs(_, ax, plot_data: Evolution, **_1):  # todo defined by paolo
    """Plot the voltage variation on the output nodes"""

    # get sequence of voltage on each output node
    data = dict([(load, []) for load, _ in plot_data.loads])
    for graph in [g for g, _ in plot_data.network_instances]:
        for load, _ in plot_data.loads:
            data[load].append(graph.nodes[load]["V"])

    __line_graph(ax, plot_data.update_times, *data.values())


def __line_graph(ax, x, *data):
    plt.cla()

    colors = iter(['b', 'g', 'r', 'c', 'm', 'y'] * len(data))
    for data, color in zip(data, colors):
        ax.plot(x, data, color=color)
        ax.tick_params(axis='y', labelcolor=color)

        # instantiate a second axes that shares the same x-axis
        ax = ax.twinx()


def __draw_network(
        graph: Graph,
        sources: Set[int], grounds: Set[int], loads: Set[int],
        edge_min: float = None, edge_max: float = None,
        normal_sizes: Any = 20,
        normal_node_colors: Any = '#1f78b4', normal_edge_colors: Any = 'k',
        **others
):
    nx.draw_networkx(
        graph,
        __nodes_positions(graph),
        **__dicts(
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
        nx.draw_networkx_nodes(
            graph,
            __nodes_positions(graph),
            **__dicts(
                others['others'] if 'others' in others else {},
                nodelist=data, node_size=300, node_color=color, alpha=0.5
            )
        )


@cache
def __nodes_positions(graph: Graph):
    return nx.get_node_attributes(graph, 'pos')


@cache
def __list_connected_components(graph: Graph):
    """Return sorted list of connected components"""
    return sorted(nx.connected_components(graph), key=len, reverse=True)


def __dicts(new, **default):
    return default | new
