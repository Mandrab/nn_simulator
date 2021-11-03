# -*- coding: utf-8 -*-
"""
@author: milan
"""
import collections

import matplotlib

from view.plotting import draw_wires, draw_junctions

from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt

import logging
import networkx as nx

logging.getLogger('matplotlib.font_manager').disabled = True
logging.getLogger('matplotlib.colorbar').disabled = True


# FUNCTIONS

def plot(device, datasheet, filler, labelize=False, square=True):
    fig, ax = plt.subplots()
    fig.set_size_inches(10, 10)

    filler(ax, device, datasheet)

    if labelize:
        ax.set_xlabel(r'x ($\mu$m)')
        ax.set_ylabel(r'y ($\mu$m)')
        ax.ticklabel_format(style='plain', axis='x', scilimits=(0, 0))
        ax.ticklabel_format(style='plain', axis='y', scilimits=(0, 0))

    if square:
        ax.set_aspect(1)  # set aspect ratio to 1

    plt.show()


# %% ############################# - PLOTS - ###################################

# Plot 1 - NW network
def adj_matrix(_, device):
    wires_dict = device.network
    plt.imshow(wires_dict['adj_matrix'], cmap='binary')
    plt.colorbar()


def network(ax, device, datasheet):
    # Plot pretty pictures of what we just did

    ax.add_patch(Rectangle((0, 0), datasheet.Lx, datasheet.Ly, color=(0.9, 0.9, 0.9), alpha=0.77))
    ax = draw_wires(ax, device.network)
    ax = draw_junctions(ax, device.network)

    ax.axis([-.1 * datasheet.Lx, 1.1 * datasheet.Lx, -.1 * datasheet.Lx,
             1.1 * datasheet.Lx])  # add some space around the unit square
    ax.set_title('Nanowires distribution')
    ax.grid()


def network_graph(ax, device, datasheet):
    # Plot pretty pictures of what we just did

    pos = nx.get_node_attributes(device.graph, 'pos')

    ax.axis([-.1 * datasheet.Lx, 1.1 * datasheet.Lx, -.1 * datasheet.Lx,
             1.1 * datasheet.Lx])  # add some space around the unit square
    ax.set_title('Nanowires distribution graph')

    nx.draw_networkx(device.graph, pos, node_color='r', node_size=20, with_labels=True)
    ax.grid()


def network_graph_kamada_kawai(ax, device, datasheet):
    ax.set_title('kamada_kawai')
    nx.draw_kamada_kawai(device.graph, node_color='r', node_size=20, with_labels=False)
    ax.grid()


def degree_of_nodes(ax, device, datasheet):
    degree_sequence = sorted([d for n, d in device.graph.degree()], reverse=True)  # degree sequence
    # print "Degree sequence", degree_sequence
    degreeCount = collections.Counter(degree_sequence)
    deg, cnt = zip(*degreeCount.items())

    # plt.hist(degree_sequence, bins = np.arange(min(degree_sequence), max(degree_sequence) + 1, 0.5))

    plt.bar(deg, cnt, width=0.8, color='b', align='center')

    plt.title("Degree Histogram")
    plt.ylabel("Count")
    plt.xlabel("Degree")
    ax.set_xticks([d for d in deg])
    ax.set_xticklabels(deg)


# todo chiamata dopo funzione di prima
##List of connected components for following graphs
# list_connected_components = sorted(nx.connected_components(device.graph),key = len, reverse = True)

def network_5(ax, device, datasheet):
    pos = nx.get_node_attributes(device.graph, 'pos')

    ax.axis([-.1 * datasheet.Lx, 1.1 * datasheet.Lx, -.1 * datasheet.Lx,
             1.1 * datasheet.Lx])  # add some space around the unit square
    ax.set_title('Connected components')

    n = round(len(list_connected_components) / 5) + 1
    colors = ['g', 'b', 'c', 'm', 'y'] * n
    colors.insert(0, 'r')

    for i in range(0, len(list_connected_components)):
        a = [x for x in list_connected_components[i]]
        if len(a) == 1:
            device.graph.nodes[a[0]]['component_color'] = 'k'
        else:
            for n in range(0, len(a)):
                device.graph.nodes[a[n]]['component_color'] = colors[i]

    nx.draw_networkx(device.graph, pos,
                     node_color=[device.graph.nodes[u]['component_color'] for u in device.graph.nodes()], node_size=20,
                     with_labels=False, Hold=True)
    ax.grid()


def largest_connected_component(ax, device, datasheet):
    K = device.graph.copy()
    largest_cc = max(nx.connected_components(device.graph), key=len)
    removed_nodes = [n for n in device.graph.nodes() if n not in largest_cc]
    K.remove_nodes_from(removed_nodes)

    pos = nx.get_node_attributes(K, 'pos')

    ax.axis([-.1 * datasheet.Lx, 1.1 * datasheet.Lx, -.1 * datasheet.Lx,
             1.1 * datasheet.Lx])  # add some space around the unit square
    ax.set_title('Nanowires distribution graph')

    nx.draw_networkx(K,pos, node_color = 'r',node_size = 20, with_labels = True)
    ax.grid()


def network_7(ax, device, datasheet):
    pos = nx.get_node_attributes(device.graph, 'pos')

    ax.axis([-.1 * datasheet.Lx, 1.1 * datasheet.Lx, -.1 * datasheet.Lx,
             1.1 * datasheet.Lx])  # add some space around the unit square
    ax.set_title('Connected components')

    list_connected_components = sorted(nx.connected_components(device.graph), key=len, reverse=True)
    n = round(len(list_connected_components) / 5) + 1
    colors = ['lightgray', 'lightgray', 'lightgray', 'lightgray', 'lightgray'] * n
    colors.insert(0, 'b')

    for i in range(0, len(list_connected_components)):
        a = [x for x in list_connected_components[i]]
        if len(a) == 1:
            device.graph.nodes[a[0]]['component_color'] = 'lightgray'
        else:
            for n in range(0, len(a)):
                device.graph.nodes[a[n]]['component_color'] = colors[i]

    nx.draw_networkx(
        device.graph,
        pos,
        node_color = [device.graph.nodes[u]['component_color'] for u in device.graph.nodes()],
        node_size = 20,
        with_labels = False
    )

    nx.draw_networkx_nodes(
        device.graph,pos,
        nodelist = [sourcenode],
        node_color = 'r',
        node_size = 300,
        alpha = 0.5
   )

    nx.draw_networkx_nodes(
        device.graph,pos,
        nodelist = [groundnode],
        node_color = 'k',
        node_size = 300,
        alpha = 0.5
    )


def conductance(ax, device, datasheet):
    color = 'tab:red'
    ax1.set_xlabel('time (s)')
    ax1.set_ylabel('Input Voltage (V)', color=color)
    ax1.plot([x for x in range(0, S.time)], V_list, color=color)
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

    color = 'tab:blue'
    ax2.set_ylabel('Conductance (S)', color=color)  # we already handled the x-label with ax1
    ax2.plot(t_list, Ynetwork_list, color=color)
    ax2.tick_params(axis='y', labelcolor=color)

    fig.tight_layout()  # otherwise the right y-label is slightly clipped

    plt.title('Network conductance')
    plt.savefig('Conductance.png')


###############################################################################

def voltage_distribution_map(ax, device, datasheet):
    timestamp_map = 0

    L = S.H[timestamp_map].copy()

    pos = nx.get_node_attributes(L, 'pos')

    ax.axis([-.1 * datasheet.Lx, 1.1 * datasheet.Lx, -.1 * datasheet.Lx,
             1.1 * datasheet.Lx])  # add some space around the unit square
    ax.set_title('Nanowires distribution graph')

    nx.draw_networkx(
        L, pos,
        node_size = 20,
        node_color = [L.nodes[n]['V'] for n in L.nodes()],
        cmap = plt.cm.plasma,   #viridis  #jet #Blues
        #edge_color = [L[u][v]['Y'] for u,v in L.edges()],
        #width = 2,
        #edge_cmap = plt.cm.Reds,
        #edge_vmin = Y_min,
        #edge_vmax = Y_max,
        arrows = False,
        with_labels = False,font_size = 6,
    )

    nx.draw_networkx_nodes(
        L,pos,
        nodelist = [mapping[sourcenode]],
        node_color = 'r',
        node_size = 300,
        alpha = 0.5
    )

    nx.draw_networkx_nodes(
        L,pos,
        nodelist = [mapping[groundnode]],
        node_color = 'k',
        node_size = 300,
        alpha = 0.5
    )


def conductance_map(ax, _, datasheet):
    timestamp_map = 0  # todo 80

    L = S.H[timestamp_map].copy()

    pos = nx.get_node_attributes(L, 'pos')

    
    
    
    ax.axis([-.1 * datasheet.Lx, 1.1 * datasheet.Lx, -.1 * datasheet.Lx,
             1.1 * datasheet.Lx])  # add some space around the unit square
    ax.set_title('Nanowires distribution graph')

    # todo nx.draw_networkx(L, pos,
    # node_size = 20,
    # node_color = [L.nodes[n]['V'] for n in L.nodes()],
    # cmap = plt.cm.Blues,
    # edge_color = [L[u][v]['Y'] for u,v in L.edges()],
    # width = 2,
    # edge_cmap = plt.cm.Reds,
    # edge_vmin = Y_min,
    # edge_vmax = Y_max,
    # arrows = False,
    # with_labels = False,font_size = 6,)

    # todo nx.draw_networkx_nodes(L,pos,
    #     nodelist = [mapping[sourcenode]],
    #     node_color = 'r',
    #     node_size = 300,
    # alpha = 0.5)

    # todo nx.draw_networkx_nodes(L,pos,
    #     nodelist = [mapping[groundnode]],
    #     node_color = 'k',
    #     node_size = 300,
    # alpha = 0.5)


def information_centrality_map(ax, device, datasheet):
    timestamp_map = 0  # todo 80

    L = S.H[timestamp_map].copy()

    pos = nx.get_node_attributes(L, 'pos')

    
    
    
    ax.axis([-.1 * datasheet.Lx, 1.1 * datasheet.Lx, -.1 * datasheet.Lx,
             1.1 * datasheet.Lx])  # add some space around the unit square
    ax.set_title('Nanowires distribution graph')

    # scaling information centrality to node sizes

    Information_centrality_list = information_centrality(S.H)

    min_information_centrality = min([min(element) for element in Information_centrality_list])
    max_information_centrality = max([max(element) for element in Information_centrality_list])

    min_node_size = 0.0001
    max_node_size = 60

    m = (max_node_size - min_node_size) / (max_information_centrality - min_information_centrality)
    b = max_node_size - (m * max_information_centrality)

    centrality_normalized = [[] for t in range(0, len(Information_centrality_list[timestamp_map]))]

    for i in range(0, len(Information_centrality_list[timestamp_map])):
        centrality_normalized[i] = (m * Information_centrality_list[timestamp_map][i]) + b

    # todo nx.draw_networkx(L, pos,
    # node_size = centrality_normalized,
    # node_color = [L.nodes[n]['information_centrality'] for n in L.nodes()],
    # cmap = plt.cm.cool,
    # edge_color = [L[u][v]['Y'] for u,v in L.edges()],
    # width = 2,
    # edge_cmap = plt.cm.Reds,
    # edge_vmin = Y_min,
    # edge_vmax = Y_max,
    # arrows = False,
    # with_labels = False,font_size = 6,)

    # todo nx.draw_networkx_nodes(L,pos,
    #     nodelist = [mapping[sourcenode]],
    #     node_color = 'r',
    #     node_size = 300,
    # alpha = 0.5)

    # todo nx.draw_networkx_nodes(L,pos,
    #     nodelist = [mapping[groundnode]],
    #     node_color = 'k',
    #     node_size = 300,
    # alpha = 0.5)


# %% ANIMATION 1 (draw_networkx function)
def animation(ax, device, datasheet):
    ### Parameters

    frames_num = timesteps
    frames_interval = 1500

    fig3, ax = plt.subplots(figsize=(10, 10))

    ### Update function

    def update(i):
        plt.cla()

        pos = nx.get_node_attributes(H_list[i], 'pos')

        # todo nx.draw_networkx(H_list[i], pos, 
        # #NODES
        # node_size = 60,
        # node_color = [H_list[i].nodes[n]['V'] for n in H_list[i].nodes()],
        # cmap = plt.cm.Blues,
        # vmin = -5,
        # vmax = 10,
        # #EDGES
        # width = 4,
        # edge_color = [H_list[i][u][v]['Y'] for u,v in H_list[i].edges()],
        # edge_cmap = plt.cm.Reds,
        # edge_vmin = Y_min,
        # edge_vmax = Y_max,
        # with_labels = False,   #Set TRUE to see node numbers
        # font_size = 6,)

        ax.set_title("t = {}".format(round(t_list[i], 1)))

    ### Animation
    anim = matplotlib.animation.FuncAnimation(fig3, update, frames=frames_num, interval=frames_interval, blit=False,
                                              repeat=True)

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
