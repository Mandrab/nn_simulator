# -*- coding: utf-8 -*-
from collections import Counter
from functools import reduce
from itertools import product, chain, cycle
from matplotlib.animation import FuncAnimation, ImageMagickWriter
from ..model.analysis.evolution import Evolution
from ..model.device.utils import largest_component
from .utils import *
from typing import Any, Callable, Iterable


def plot(data: Evolution, filler: Callable[[Any, Any, Evolution], None]):
    """Standard plotting setup."""

    fig = plt.figure(figsize=(10, 10))
    ax = fig.subplots()

    # set axes labels, grid and add some space around the unit square
    ax.set(title=filler.__name__.capitalize().replace('_', ' '))
    ax.set(xlabel=r'x ($\mu$m)', ylabel=r'y ($\mu$m)')
    ax.ticklabel_format(style='plain')
    ax.grid()
    def _(iterable: Iterable): return reduce(lambda a, b: a * b, iterable)
    ax.axis(map(_, product([data.datasheet.Lx, data.datasheet.Ly], [-.1, 1.1])))

    # add data to plot
    filler(fig, ax, data)
    return plt


def adjacency_matrix(_0, _1, plot_data: Evolution, **_2):
    plt.imshow(plot_data.wires_dict['adj_matrix'], cmap='binary')


def nanowires_distribution(_0, ax, plot_data: Evolution, **_1):
    draw_wires(ax, plot_data.wires_dict)
    draw_junctions(ax, plot_data.wires_dict)


def enumerated_nanowires_distribution(_0, _1, plot_data: Evolution, **others):
    draw(plot_data.graph, others, 'r', label=True)


def graph_of_the_network_Kamada_Kawai(_0, _1, plot_data: Evolution, **others):
    plt.cla()  # override default axis config
    nx.draw_kamada_kawai(
        plot_data.graph,
        **dicts(others, node_color='r', node_size=20, with_labels=False)
    )


def degree_of_nodes_histogram(_0, ax, plot_data: Evolution, **_1):
    plt.cla()  # override default axis config

    degrees = [*plot_data.graph.degree]
    degree_count = Counter(sorted([d for _, d in degrees], reverse=True))
    deg, cnt = zip(*degree_count.items())

    plt.bar(deg, cnt, width=0.8, color='b', align='center')
    ax.set(ylabel='Count', xlabel='Degree', xticks=deg, xticklabels=deg)


def connected_components(_0, _1, plot_data: Evolution, **others):
    components = list_connected_components(plot_data.graph)
    colors = chain('r', cycle(['g', 'b', 'c', 'm', 'y']))

    # set node-color for print (different between components)
    colors = zip(components, colors)
    colors = [(a, 'k' if len(a) == 1 else b) for a, b in colors]
    colors = [list(product(ns, [c])) for ns, c in colors]
    colors = [color for _, color in sorted(chain(*colors))]

    draw(plot_data.graph, others, colors)


def labeled_network(_0, _1, plot_data: Evolution, **others):
    draw(largest_component(plot_data.graph), others, 'r', label=True)


def largest_connected_component(_0, _1, data: Evolution, **others):
    graph, out, source, load = data.graph, data.grounds, data.inputs, data.loads
    opt = iter(getattr(others, _, {}) for _ in ['default', 'inputs', 'loads'])

    components = list_connected_components(graph)
    colors = chain('b', cycle(['lightgray']))

    # set node-color for print (different between components)
    colors = [list(product(ns, [c])) for ns, c in zip(components, colors)]
    colors = [color for _, color in sorted(chain(*colors))]

    # todo makes no sense if input change in time
    draw(graph, next(opt), colors)
    highlight(graph, {k for k, _ in source}, 'r', next(opt))
    highlight(graph, out | {*dict(load)}, 'k', next(opt))


def network_conductance(fig, ax1, plot_data: Evolution, **_1):
    """Display the max conductivity of a path in the network for each state"""
    plt.cla()  # override default axis config

    # calculate network minimum resistance
    resistances = [
        min([
            (source, nx.resistance_distance(
                graph,
                source,
                # todo
                [*plot_data.grounds | {n for n, _ in plot_data.loads}][0],
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


def voltage_distribution(_, ax, plot_data: Evolution, **others):
    """Plot the voltage distribution (intensity) of the initial graph"""
    graph = next(iter(plot_data.currents_graphs())).copy()
    draw_network(
        graph,
        plot_data.sources, plot_data.grounds, {n for n, _ in plot_data.loads},
        plot_data.datasheet.Y_min, plot_data.datasheet.Y_max,
        normal_node_colors=[graph.nodes[n]['V'] for n in graph.nodes()],
        **dicts(others, default=dict(ax=ax), others=dict(ax=ax))
    )


def conductance_distribution(_, ax, plot_data: Evolution, **others):
    """Plot the conductance distribution of the final graph"""
    graph = next(iter(plot_data.currents_graphs(reverse=True))).copy()
    draw_network(
        graph,
        plot_data.sources, plot_data.grounds, {n for n, _ in plot_data.loads},
        plot_data.datasheet.Y_min, plot_data.datasheet.Y_max, 20,
        [graph.nodes[n]['V'] for n in graph.nodes()],
        [graph[u][v]['Y'] for u, v in graph.edges()],
        **dicts(others, default=dict(ax=ax), others=dict(ax=ax))
    )


def information_centrality(_, ax, plot_data: Evolution, **others):
    """Plot the information centrality of the final graph"""

    # scaling information centrality to node sizes
    centrality = [*plot_data.information_centrality()]
    L = centrality[-1]

    min_centrality = min([min(element) for element in centrality])
    max_centrality = max([max(element) for element in centrality])

    min_node_size, max_node_size = 1e-3, 60

    m = (max_node_size - min_node_size) / (max_centrality - min_centrality)
    b = max_node_size - (m * max_centrality)

    centrality_normalized = [(m * v) + b for v in centrality[-1]]

    draw_network(
        plot_data.graph,
        plot_data.sources, plot_data.grounds, {n for n, _ in plot_data.loads},
        plot_data.datasheet.Y_min, plot_data.datasheet.Y_max,
        centrality_normalized,
        [L.nodes[n]['information_centrality'] for n in L.nodes],
        [L[u][v]['Y'] for u, v in L.edges()],
        **dicts(others, default=dict(ax=ax), others=dict(ax=ax))
    )


def animation(fig, ax, plot_data: Evolution, **others):
    """Plot animated conductance evolution"""
    frames = len(plot_data.network_instances) - 1

    hs = [*plot_data.currents_graphs()]

    def update(i):
        plt.cla()

        nx.draw_networkx(
            hs[i],
            nodes_positions(hs[i]),
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
        **dicts(others, frames=frames, interval=500, blit=False, repeat=True)
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
        **dicts(others, frames=frames, interval=500, blit=False, repeat=True)
    ).save('animation_2.gif', writer=ImageMagickWriter(fps=2))


def outputs(_, ax, plot_data: Evolution, **_1):  # todo defined by paolo
    """Plot the voltage variation on the output nodes"""

    # get sequence of voltage on each output node
    data = dict([(load, []) for load, _ in plot_data.loads])
    for graph in [g for g, _ in plot_data.network_instances]:
        for load, _ in plot_data.loads:
            data[load].append(graph.nodes[load]["V"])

    line_graph(ax, plot_data.update_times, *data.values())
