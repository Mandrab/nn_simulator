from model import wires
from model.functions import *

import logging
import networkx as nx

# NETWORK GENERATION
def generate(
    wires_count,
    mean_length,
    standard_length,
    centroid_dispersion,
    seed,
    Lx,
    Ly
):
    logging.debug('Generating network')

    # generate the network
    wires_dict = wires.generate_wires_distribution(
        number_of_wires = wires_count,
        wire_av_length = mean_length,
        wire_dispersion = standard_length,
        gennorm_shape = 10,
        centroid_dispersion = centroid_dispersion,
        this_seed = seed,
        Lx = Lx,
        Ly = Ly
    )

    # get junctions list and their positions
    wires.detect_junctions(wires_dict)

    # genreate graph object and adjacency matrix
    wires.generate_graph(wires_dict)

    return wires_dict

# GRAPH GENERATION
def get_graph(wires_dict):
    logging.debug('Extracting graph from network')

    Adj_matrix = wires_dict['adj_matrix']

    # complete graph with also unconnected nodes
    G = nx.from_numpy_matrix(Adj_matrix)

    xpos = [x for x in wires_dict['xc']]
    ypos = [y for y in wires_dict['yc']]

    xjpos = [x for x in wires_dict['xi']]
    yjpos = [y for y in wires_dict['yi']]

    # add node and junction positions as graph attributes (from dictionary)
    for n in G.nodes():
        G.nodes[n]['pos'] = (xpos[n],ypos[n])

    n = 0
    for u,v in G.edges():
        G[u][v]['jx_pos'] = (xjpos[n],yjpos[n])
        n = n+1

    '''
    #list of wire lengths
    wire_lengths = xpos = [x for x in wires_dict['wire_lengths']]
    '''

    return G
