from . import wires
from config_model import *
from functions import *

import logging
import networkx as nx
import sys

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

# COMPONENT EXTRACTION
def largest_component(graph):
    logging.debug('Largest component extraction')

    component = graph.copy()
    largest_cc = max(nx.connected_components(graph), key = len)
    unconnected_nodes = [n for n in graph.nodes() if n not in largest_cc]
    component.remove_nodes_from(unconnected_nodes)
    return component

# SOURCE-GROUND CONNECTED NODES EXTRACTION
def connected_nodes(graph):
    logging.debug('Connected (source & ground) nodes extraction')

    # make a graph K with only nodes connected to source and ground nodes
    component = graph.copy()

    # remove nodes not connected to the groundnode (and sourcenode)
    removed_nodes = [n for n in graph.nodes() if not nx.has_path(graph, n, groundnode)]
    component.remove_nodes_from(removed_nodes)
    return component

# ELECTRICAL STIMULATION
def stimulate(G):

    if nx.has_path(G, sourcenode, groundnode) is False:
        print('Source and ground node are NOT connected! Stimulation is not possible!')
        sys.exit()

    ###############################################################################

    # select connected graph (between source and ground node)
    K = connected_nodes(G)

    # relable node names (for mod_voltage node analysis)
    M = K.copy()
    mapping = dict(zip(M, range(0, K.number_of_nodes()))) 
    M = nx.relabel_nodes(M, mapping)

    ###############################################################################

    # ELECTRICAL STIMULATION
    logging.debug('Electrical stimulation of the network')

    x = 10      # pulse amplitude
    n = 1       # number of pulses
    k = 80      # number of read

    Vin_list = [0.01]
    Vstim_list = [x,x,x,x,x,x,x,x,x,x]*n
    Vread_list = [0.01]*k # [0.01, 0.01, ..., 0.01]

    Vin_list.extend(Vstim_list)
    Vin_list.extend(Vread_list)

    # TIMING
    delta_t = [0]
    delta_t_stim = [0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.05]*n
    delta_t_read = [0.05]*k

    delta_t.extend(delta_t_stim)
    delta_t.extend(delta_t_read)

    timesteps = len(delta_t)

    ###############################################################################

    # GROWTH OF THE CONDUCTIVE PATH
    logging.debug('Growth of the conductive path')

    M = initialize_graph_attributes(M,Y_min)

    M_bis = M.copy()    ##check for nx.resistance_distance

    M.nodes[mapping[sourcenode]]['source_node'] = True
    M.nodes[mapping[groundnode]]['ground_node'] = True

    ####Initialization of list over time      
    t_list = [[] for t in range(0,timesteps)]                                                     
    H_list = [[] for t in range(0,timesteps)]
    I_list = [[] for t in range(0,timesteps)]
    V_list = [[] for t in range(0,timesteps)]                              #list of graphs over time 

    Rnetwork_list = [[] for t in range(0,timesteps)]
    Ynetwork_list = [[] for t in range(0,timesteps)]

    Shortest_path_length_network_list = [[] for t in range(0,timesteps)]

    ####Pristine state                           

    t_list[0] = 0

    H_list[0] = mod_voltage_node_analysis(M, Vin_list[0], mapping[sourcenode], mapping[groundnode])
    I_list[0] = calculate_Isource(H_list[0], mapping[sourcenode])
    V_list[0] = calculate_Vsource(H_list[0], mapping[sourcenode])

    nx.set_node_attributes(H_list[0], nx.information_centrality(M, weight = 'Y'), "information_centrality")

    Rnetwork_list[0] = calculate_network_resistance(H_list[0], mapping[sourcenode])
    Ynetwork_list[0] = 1/Rnetwork_list[0]

    Shortest_path_length_network_list[0] = nx.shortest_path_length(H_list[0], source = mapping[sourcenode], target = mapping[groundnode], weight = 'R') ##Shortest path resistance

    ####Growth over time
    for i in range(1, int(timesteps)):

        t_list[i] = t_list[i-1]+delta_t[i]
        
        update_edge_weigths(M,delta_t[i],Y_min, Y_max,kp0,eta_p,kd0,eta_d) 
        
        H_list[i] = mod_voltage_node_analysis(M, Vin_list[i], mapping[sourcenode], mapping[groundnode])
        I_list[i] = calculate_Isource(H_list[i], mapping[sourcenode])
        V_list[i] = calculate_Vsource(H_list[i], mapping[sourcenode])
        
        nx.set_node_attributes(H_list[i], nx.information_centrality(M, weight = 'Y'), "information_centrality")
        
    #Rnetwork_list[i] = calculate_network_resistance(H_list[i], mapping[sourcenode])
        Rnetwork_list[i] = nx.resistance_distance(M,mapping[sourcenode], mapping[groundnode], weight = 'Y', invert_weight = False)   
        Ynetwork_list[i] = 1/Rnetwork_list[i]
        
        Shortest_path_length_network_list[i] = nx.shortest_path_length(M, source = mapping[sourcenode], target = mapping[groundnode], weight = 'R')
    ############################################################################# 

    # Evolution of information centrality
    logging.debug('Evolution of information centrality')

    Information_centrality_list = [[] for t in range(0,timesteps)]     
        
    for i in range(0,timesteps):   
        centrality = nx.get_node_attributes(H_list[i],'information_centrality')
        Information_centrality_list[i] = list(centrality.values())

    return G