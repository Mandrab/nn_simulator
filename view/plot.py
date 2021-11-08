# -*- coding: utf-8 -*-
"""
@author: milan
"""
import collections
import logging
import matplotlib.pyplot as plt
import networkx as nx

from functools import cache
from matplotlib.animation import FuncAnimation

from model.analysis.evolution import Evolution
from model.device.utils import largest_component
from view.plotting import draw_wires, draw_junctions

logging.getLogger('matplotlib.font_manager').disabled = True
logging.getLogger('matplotlib.colorbar').disabled = True


def plot(data: Evolution, filler):
    """Standard plotting setup"""

    fig, ax = plt.subplots()
    fig.set_size_inches(10, 10)

    # add some space around the unit square
    ax.axis([
        -.1 * data.datasheet.Lx,
        1.1 * data.datasheet.Lx,
        -.1 * data.datasheet.Ly,
        1.1 * data.datasheet.Ly
    ])

    # set axes labels
    ax.set_xlabel(r'x ($\mu$m)')
    ax.set_ylabel(r'y ($\mu$m)')
    ax.ticklabel_format(style='plain', axis='x', scilimits=(0, 0))
    ax.ticklabel_format(style='plain', axis='y', scilimits=(0, 0))

    # show plot grid
    ax.grid()

    # add data to plot
    filler(fig, ax, data)

    plt.show()


# %% ############################# - PLOTS - ###################################

def adj_matrix(_0, _1, plot_data):
    """Plot adjacency matrix"""

    plt.imshow(plot_data.wires_dict['adj_matrix'], cmap='binary')
    plt.colorbar()


def network(_, ax, plot_data):
    """Plot nano-wires distribution from wires_dict (network)"""

    ax.set_title('Nano-wires distribution')

    draw_wires(ax, plot_data.wires_dict)
    draw_junctions(ax, plot_data.wires_dict)


def graph(_, ax, plot_data):
    """Plot nano-wires distribution from graph"""

    ax.set_title('Nano-wires distribution graph')

    nx.draw_networkx(
        plot_data.graph,
        nx.get_node_attributes(plot_data.graph, 'pos'),
        node_color='r',
        node_size=20,
        with_labels=True
    )


def kamada_kawai_graph(_, ax, plot_data):
    """Plot nano-wires distribution from graph (kamada-style)"""

    plt.cla()  # override default axis config

    ax.set_title('Nano-wires distribution graph (kamada kawai)')

    nx.draw_kamada_kawai(
        plot_data.graph,
        node_color='r',
        node_size=20,
        with_labels=False
    )


def degree_of_nodes(_, ax, plot_data):
    """Print a diagram representing, for each degree, its quantity"""

    plt.cla()  # override default axis config

    ax.set_title("Degree Histogram")

    # print "Degree sequence", degree_sequence
    degree_count = collections.Counter(
        sorted([d for n, d in plot_data.graph.degree()], reverse=True)
    ).items()
    deg, cnt = zip(*degree_count)

    plt.bar(deg, cnt, width=0.8, color='b', align='center')

    plt.ylabel("Count")
    plt.xlabel("Degree")
    ax.set_xticks([d for d in deg])
    ax.set_xticklabels(deg)


@cache
def __list_connected_components(graph):
    """Return sorted list of connected components"""

    return sorted(nx.connected_components(graph), key=len, reverse=True)


def highlight_connected_components(_, ax, plot_data):
    """Print connected components in the network (different colors for each)"""

    ax.set_title('Connected components')

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
        node_color=[plot_data.graph.nodes[u]['component_color'] for u in
                    plot_data.graph.nodes()],
        node_size=20,
        with_labels=False
    )


def largest_connected_component(_, ax, plot_data):
    """Plot only the largest connected component"""

    ax.set_title('Nanowires distribution graph')

    graph = largest_component(plot_data.graph)
    pos = nx.get_node_attributes(graph, 'pos')

    nx.draw_networkx(graph, pos, node_color='r', node_size=20, with_labels=True)


def network_7(_, ax, plot_data):
    """Print connected components in the network (different colors for each)"""
    # todo difference from 'highlight_connected_components'?

    ax.set_title('Connected components')

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

    pos = nx.get_node_attributes(plot_data.graph, 'pos')

    nx.draw_networkx(
        plot_data.graph,
        pos,
        node_color=[
            plot_data.graph.nodes[node]['component_color']
            for node in plot_data.graph.nodes()
        ],
        node_size=20,
        with_labels=False
    )

    nx.draw_networkx_nodes(
        plot_data.graph,
        pos,
        nodelist=[*map(lambda v: v[0], plot_data.inputs)],
        # todo makes no sense if input change in time
        node_color='r',
        node_size=300,
        alpha=0.5
    )

    nx.draw_networkx_nodes(
        plot_data.graph,
        pos,
        nodelist=[plot_data.ground],
        node_color='k',
        node_size=300,
        alpha=0.5
    )


def conductance(fig, ax1, plot_data):
    """Display the max conductivity of a path in the network for each state"""

    plt.cla()  # override default axis config

    # extract time sequence
    t_list = [
        x * plot_data.delta_t
        for x in range(len(plot_data.network_instances))
    ]

    # calculate network minimum resistance
    resistances = [
        min([
            (source, nx.resistance_distance(
                graph,
                source,
                plot_data.ground,
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

    ax1.plot(t_list, sources_voltages, color=color)
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

    color = 'tab:blue'
    ax2.set_ylabel('Conductance (S)',
                   color=color)  # we already handled the x-label with ax1

    ax2.plot(t_list, conductances, color=color)
    ax2.tick_params(axis='y', labelcolor=color)

    fig.tight_layout()  # otherwise the right y-label is slightly clipped

    plt.title('Network conductance')


def voltage_distribution_map(_, ax, plot_data):
    """Plot the voltage distribution (intensity) of the initial graph"""  # todo

    ax.set_title('Nano-wires distribution graph')

    L = next(plot_data.currents_graphs()).copy()

    pos = nx.get_node_attributes(L, 'pos')

    nx.draw_networkx(
        L,
        pos,
        node_size=20,
        node_color=[L.nodes[n]['V'] for n in L.nodes()],
        cmap=plt.cm.plasma,  # viridis  #jet #Blues
        # edge_color = [L[u][v]['Y'] for u,v in L.edges()],
        # width = 2,
        # edge_cmap = plt.cm.Reds,
        # edge_vmin = Y_min,
        # edge_vmax = Y_max,
        arrows=False,
        with_labels=False,
        font_size=6
    )

    sources = [s for s, _ in plot_data.network_instances[0][1]]
    nx.draw_networkx_nodes(
        L, pos,
        nodelist=sources,
        node_color='r',
        node_size=300,
        alpha=0.5
    )

    nx.draw_networkx_nodes(
        L, pos,
        nodelist=[plot_data.ground],
        node_color='k',
        node_size=300,
        alpha=0.5
    )


def conductance_map(_, ax, plot_data):
    """Plot the conductance distribution of the final graph"""  # todo

    ax.set_title('Nano-wires distribution graph')

    L = next(plot_data.currents_graphs(reverse=True)).copy()

    pos = nx.get_node_attributes(L, 'pos')

    nx.draw_networkx(
        L,
        pos,
        node_size=20,
        node_color=[L.nodes[n]['V'] for n in L.nodes()],
        cmap=plt.cm.Blues,
        edge_color=[L[u][v]['Y'] for u, v in L.edges()],
        width=2,
        edge_cmap=plt.cm.Reds,
        edge_vmin=plot_data.datasheet.Y_min,
        edge_vmax=plot_data.datasheet.Y_max,
        arrows=False,
        with_labels=False,
        font_size=6
    )

    sources = [s for s, _ in plot_data.network_instances[-1][1]]
    nx.draw_networkx_nodes(
        L,
        pos,
        nodelist=sources,
        node_color='r',
        node_size=300,
        alpha=0.5
    )

    nx.draw_networkx_nodes(
        L,
        pos,
        nodelist=[plot_data.ground],
        node_color='k',
        node_size=300,
        alpha=0.5
    )


def information_centrality_map(_, ax, plot_data):
    """Plot the information centrality of the final graph"""  # todo

    ax.set_title('Nano-wires distribution graph')

    L = next(plot_data.currents_graphs(reverse=True)).copy()

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

    pos = nx.get_node_attributes(L, 'pos')

    nx.draw_networkx(
        L,
        pos,
        node_size=centrality_normalized,
        node_color=[
            L.nodes[n]['information_centrality']
            for n in L.nodes()
        ],
        cmap=plt.cm.cool,
        edge_color=[L[u][v]['Y'] for u, v in L.edges()],
        width=2,
        edge_cmap=plt.cm.Reds,
        edge_vmin=plot_data.datasheet.Y_min,
        edge_vmax=plot_data.datasheet.Y_max,
        arrows=False,
        with_labels=False, font_size=6
    )

    sources = [s for s, _ in plot_data.network_instances[-1][1]]
    nx.draw_networkx_nodes(
        L,
        pos,
        nodelist=sources,
        node_color='r',
        node_size=300,
        alpha=0.5
    )

    nx.draw_networkx_nodes(
        L,
        pos,
        nodelist=[plot_data.ground],
        node_color='k',
        node_size=300,
        alpha=0.5
    )


def animation(fig, ax, plot_data):
    """Plot animated evolution"""

    frames_num = len(plot_data.network_instances) -1

    frames_interval = 1500

    hs = [*plot_data.currents_graphs()]
    t_list = [i * plot_data.delta_t for i in range(frames_num)]

    def update(i):
        plt.cla()

        pos = nx.get_node_attributes(hs[i], 'pos')

        nx.draw_networkx(
            hs[i],
            pos,
            # NODES
            node_size=60,
            node_color=[hs[i].nodes[n]['V'] for n in hs[i].nodes()],
            cmap=plt.cm.Blues,
            vmin=-5,
            vmax=10,
            # EDGES
            width=4,
            edge_color=[hs[i][u][v]['Y'] for u, v in hs[i].edges()],
            edge_cmap=plt.cm.Reds,
            edge_vmin=plot_data.datasheet.Y_min,
            edge_vmax=plot_data.datasheet.Y_max,
            with_labels=False,  # set TRUE to see node numbers
            font_size=6
        )

        ax.set_title("t = {}".format(round(t_list[i], 1)))

    # animation
    anim = FuncAnimation(
        fig,
        update,
        frames=frames_num,
        interval=frames_interval,
        blit=False,
        repeat=True
    )

    #plt.show()
    anim.save('animation_1.gif', writer='imagemagick')

    ###############################################################################

    '''
    #%% ANIMATION 2 (draw_kamada_kawai)

    ### Parameters

    frames_num = timesteps
    frames_interval = 1500

    fig3, ax = plt.subplots(figsize = (10,10))


    ### Update function

    def update(i):
        
        plt.cla() 
        
        
        
        nx.draw_kamada_kawai(H_list[i], 
                    #NODES
                    node_size = 60,
                    node_color = [H_list[i].nodes[n]['V'] for n in H_list[i].nodes()],
                    cmap = plt.cm.Blues,
                    vmin = -5,
                    vmax = 10,
                    #EDGES
                    width = 4,
                    edge_color = [H_list[i][u][v]['Y'] for u,v in H_list[i].edges()],
                    edge_cmap = plt.cm.Reds,
                    edge_vmin = Y_min,
                    edge_vmax = Y_max,
                    with_labels = False,   #Set TRUE to see node numbers
                    font_size = 6,)
        
        ax.set_title("t = {}".format(round(t_list[i], 1)))
        

    ### Animation
    anim = matplotlib.animation.FuncAnimation(fig3, update, frames = frames_num, interval = frames_interval, blit = False, repeat = True)

    anim.save('animation_2.gif', writer = 'imagemagick')

    ###############################################################################
    '''
