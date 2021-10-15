# -*- coding: utf-8 -*-
"""
Created on Mon Jun  1 18:26:06 2020

@author: milan
"""

import sys 

import wires
import networkx as nx
import numpy as np
import collections

# Plotting tools
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt
from matplotlib import animation
import matplotlib.animation


# Fitting tools
from scipy.optimize import curve_fit
from scipy.special import factorial
from scipy.stats import poisson

from functions import define_grid_graph,define_grid_graph_2,initialize_graph_attributes, mod_voltage_node_analysis, calculate_network_resistance, calculate_Vsource, calculate_Isource, update_edge_weigths, connected_component_subgraphs 
from plotting import draw_wires, draw_junctions, plot_0, plot_1, plot_2, plot_3, plot_4, plot_5
from networkx import algorithms

#%% NW DISTRIBUTION PARAMETERS
nwires = 1500
centroid_dispersion = 200

mean_length = 40.0
std_length = 14.0
seed = 40
Lx   = 500
Ly   = 500


plt_network_adj_matrix = 0
plot_network_1 = 1     #plot NW network
plot_network_2 = 1     #plot the NW network graph
plot_network_3 = 0     #plot the NW network graph kamada_kawai
plot_network_4 = 0
plot_network_5 = 0
plot_network_6 = 1     #plot only the largest connected component
plot_network_7 = 1

plot_conductance = 1   #Plot G-V

voltage_distribution_map = 1

conductance_map = 1

information_centrality_map = 1

animation_1 = 0

#%% MODEL PARAMETERS

##update_edge_weigths parameters
kp0=0.0001
eta_p=10
kd0=0.5
eta_d=1

Y_min=0.001                                                                  
Y_max=Y_min*100


#%% GENERATE NW DISTRIBUTION

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')


# Generate the network
wires_dict = wires.generate_wires_distribution(number_of_wires = nwires,
                                         wire_av_length = mean_length,
                                         wire_dispersion = std_length,
                                         gennorm_shape = 10,
                                         centroid_dispersion=centroid_dispersion,
                                         this_seed = seed,
                                         Lx = Lx,
                                         Ly = Ly)

# Get junctions list and their positions
wires.detect_junctions(wires_dict)

# Genreate graph object and adjacency matrix
wires.generate_graph(wires_dict)

###############################################################################

#%% GRAPH REPRESENTATION
Adj_matrix=wires_dict['adj_matrix']

G=nx.from_numpy_matrix(Adj_matrix)   #complete graph with also unconnected nodes

xpos=[x for x in wires_dict['xc']]
ypos=[y for y in wires_dict['yc']]

xjpos=[x for x in wires_dict['xi']]
yjpos=[y for y in wires_dict['yi']]

## add node and junction positions as graph attributes (from dictionary)
for n in G.nodes():
    G.nodes[n]['pos']=(xpos[n],ypos[n])

n=0
for u,v in G.edges():
    G[u][v]['jx_pos'] =(xjpos[n],yjpos[n])
    n=n+1



'''
#list of wire lengths
wire_lengths =xpos=[x for x in wires_dict['wire_lengths']]

###############################################################################


## Number of nodes
print('The number of nodes is:')
number_of_nodes=G.number_of_nodes()
print(number_of_nodes)

## Number of edges
print('The number of edges (junctions) is:')
number_of_edges=G.number_of_edges()
print(number_of_edges)

##Degree of nodes list
print('The degree of node list:')
degrees = [val for (node, val) in G.degree()]
print(degrees)

##CLustering coefficient list
print('The clustering of node list:')
a = nx.clustering(G)
clustering=[]
for n in range(0,len(a)):
    clustering.append(a[n])
print(clustering)


##Number of connected components
print('The number of connected components is:')
num_connected_components=nx.number_connected_components(G)
print(num_connected_components)


##List of connected components
list_connected_components = sorted(nx.connected_components(G),key=len, reverse=True)

##Number of nodes not connected
print('The number of isolated nodes is:')
isolated_nodes_list=[x for x in nx.isolates(G)]
print(len(isolated_nodes_list))

##Size of the largest component
Gmax_nodes = max(nx.connected_components(G), key=len)
print('The number of nodes in the largest component is:')
print(len(Gmax_nodes))



## ANALYSIS OF THE LARGEST CONNECTED COMPONENT
K=G.copy()
largest_cc = max(nx.connected_components(G), key=len)
removed_nodes= [n for n in G.nodes() if n not in largest_cc]
K.remove_nodes_from(removed_nodes)


##Diameter of the largest connected component
diameter=nx.diameter(K)
print('The diameter of the largest connected component is:')
print(diameter)

##Average shortest path length of the largest connected component
avg_shortest_path=nx.average_shortest_path_length(K, weight=None)
print('The average shortest path length of the largest connected component is:')
print(avg_shortest_path)

##Average clustering coefficient
avg_clustering_coefficient=nx.average_clustering(K)
print('The average clustering coefficient of the largest connected component is:')
print(avg_clustering_coefficient)

##Sigma small-world coefficient of the largest connected component
sigma_parameter=nx.sigma(K, niter=100, nrand=10, seed=None)
print('Sigma small-world coefficient of the largest connected component is:')
print(sigma_parameter)


##Omega small-world coefficient of the largest connected component
omega_parameter=nx.omega(K, niter=100, nrand=10, seed=None)
print('Omega small-world coefficient of the largest connected component is:')
print(omega_parameter)
'''



############################### SAVE DATA #####################################
'''
filename = "nodes_" + str(nwires) + "_junctions_" + str(number_of_edges) + "_seed_"+str(seed)+".txt"
my_data=np.vstack((degrees,clustering))
my_data=my_data.T
np.savetxt(filename,my_data, delimiter=',', header='degree,clustering',comments='')



###make a graph for gephi
Z=nx.from_numpy_matrix(Adj_matrix)
nx.write_gexf(Z, "test.gexf")

'''
#%% ELECTRICAL STIMULATION

##Source and ground node positions
sourcenode = 273                                                  
groundnode = 358

if nx.has_path(G, sourcenode, groundnode) is True:
    print('Source and ground node are connected!')
else:
    print('Source and ground node are NOT connected!')
    sys.exit()

###############################################################################

#%% SELECT CONNECTED GRAPH (between source and ground node) and relabel

## Make a graph K with only nodes connected to source and ground nodes
K=G.copy()

#remove nodes not connected to the groundnode (and sourcenode)
removed_nodes= [n for n in G.nodes() if nx.has_path(G,n, groundnode) == False]
K.remove_nodes_from(removed_nodes)

## Make a graph M with remapping of node names (for mod_voltage node analysis)
M=K.copy()
mapping = dict(zip(M, range(0, K.number_of_nodes()))) 
M = nx.relabel_nodes(M, mapping)

###############################################################################



#%% ELECTRICAL STIMULATION
    
x=10      ##pulse amplitude
n=1       ##number of pulses
k=80      ##number of read

Vin_list=[0.01]
Vstim_list=[x,x,x,x,x,x,x,x,x,x]*n
Vread_list=[0.01]*k

Vin_list.extend(Vstim_list)
Vin_list.extend(Vread_list)

##TIMING
delta_t=[0]
delta_t_stim=[0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.05]*n
delta_t_read=[0.05]*k

delta_t.extend(delta_t_stim)
delta_t.extend(delta_t_read)

timesteps= len(delta_t)

###############################################################################

#%% GROWTH OF THE CONDUCTIVE PATH

M = initialize_graph_attributes(M,Y_min)

M_bis=M.copy()    ##check for nx.resistance_distance

M.nodes[mapping[sourcenode]]['source_node']=True
M.nodes[mapping[groundnode]]['ground_node']=True


####Initialization of list over time      
t_list=[[] for t in range(0,timesteps)]                                                     
H_list=[[] for t in range(0,timesteps)]
I_list=[[] for t in range(0,timesteps)]
V_list=[[] for t in range(0,timesteps)]                              #list of graphs over time 
                                                 
Rnetwork_list=[[] for t in range(0,timesteps)]
Ynetwork_list=[[] for t in range(0,timesteps)]

Shortest_path_length_network_list=[[] for t in range(0,timesteps)]

####Pristine state                           

t_list[0] = 0

H_list[0] = mod_voltage_node_analysis(M, Vin_list[0], mapping[sourcenode], mapping[groundnode])
I_list[0] = calculate_Isource(H_list[0], mapping[sourcenode])
V_list[0] = calculate_Vsource(H_list[0], mapping[sourcenode])

nx.set_node_attributes(H_list[0], nx.information_centrality(M, weight='Y'), "information_centrality")

Rnetwork_list[0] = calculate_network_resistance(H_list[0], mapping[sourcenode])
Ynetwork_list[0] = 1/Rnetwork_list[0]

Shortest_path_length_network_list[0]=nx.shortest_path_length(H_list[0], source=mapping[sourcenode], target=mapping[groundnode], weight='R') ##Shortest path resistance


####Growth over time
for i in range(1, int(timesteps)):

    t_list[i] = t_list[i-1]+delta_t[i]
    
    update_edge_weigths(M,delta_t[i],Y_min, Y_max,kp0,eta_p,kd0,eta_d) 
    
    H_list[i] = mod_voltage_node_analysis(M, Vin_list[i], mapping[sourcenode], mapping[groundnode])
    I_list[i] = calculate_Isource(H_list[i], mapping[sourcenode])
    V_list[i] = calculate_Vsource(H_list[i], mapping[sourcenode])
    
    nx.set_node_attributes(H_list[i], nx.information_centrality(M, weight='Y'), "information_centrality")
    
   #Rnetwork_list[i] = calculate_network_resistance(H_list[i], mapping[sourcenode])
    Rnetwork_list[i]= nx.resistance_distance(M,mapping[sourcenode], mapping[groundnode], weight='Y', invert_weight=False)   
    Ynetwork_list[i] = 1/Rnetwork_list[i]
    
    Shortest_path_length_network_list[i] = nx.shortest_path_length(M, source=mapping[sourcenode], target=mapping[groundnode], weight='R')
############################################################################# 

#%% Evolution of information centrality

Information_centrality_list=[[] for t in range(0,timesteps)]     
    
for i in range(0,timesteps):   
    centrality = nx.get_node_attributes(H_list[i],'information_centrality')
    Information_centrality_list[i] = list(centrality.values())

#%% Save data (electrical part)
timestamp=0


#nodes
pos_el_nodes=nx.get_node_attributes(H_list[timestamp], 'pos')
x_pos_el=[pos_el_nodes[n][0] for n in H_list[timestamp].nodes]
y_pos_el=[pos_el_nodes[n][1] for n in H_list[timestamp].nodes]
V_list_el=[H_list[timestamp].nodes[n]['V'] for n in H_list[timestamp].nodes()]
Information_centrality_el=[H_list[timestamp].nodes[n]['information_centrality'] for n in H_list[timestamp].nodes()]


#node file
filename_el = "Electrical_data_nodes_"+"timestamp="+str(timestamp)+"_nodes_" + str(nwires) + "_seed_"+str(seed)+".txt"
my_data_el=np.vstack((x_pos_el,y_pos_el,V_list_el,Information_centrality_el))
my_data_el=my_data_el.T
np.savetxt(filename_el,my_data_el, delimiter=',', header='x_pos,y_pos,V_list, Information_centrality_list',comments='')



#edges
pos_el_jx=[H_list[timestamp].edges[u, v]['jx_pos'] for u,v in H_list[timestamp].edges()]
xj_pos_el= [pos_el_jx[n][0] for n in range(0,len(pos_el_jx))]
yj_pos_el= [pos_el_jx[n][1] for n in range(0,len(pos_el_jx))]
I_list_el=[H_list[timestamp].edges[u, v]['I'] for u,v in H_list[timestamp].edges()]
Y_list_el=[H_list[timestamp].edges[u, v]['Y'] for u,v in H_list[timestamp].edges()]
g_list_el=[H_list[timestamp].edges[u, v]['g'] for u,v in H_list[timestamp].edges()]

#edge file
filename_el_2 = "Electrical_data_edges_"+"timestamp="+str(timestamp)+"_nodes_" + str(nwires) + "_seed_"+str(seed)+".txt"
my_data_el_2=np.vstack((xj_pos_el,yj_pos_el,I_list_el,Y_list_el,g_list_el))
my_data_el_2=my_data_el_2.T
np.savetxt(filename_el_2,my_data_el_2, delimiter=',', header='xj_pos,yj_pos,I_list,Y_list,g_list',comments='')

#I-V list
filename_el_3 = "Electrical_I-V-Y-SP-data_"+"_nodes_" + str(nwires) + "_seed_"+str(seed)+".txt"
my_data_el_3=np.vstack((t_list,V_list,I_list,Rnetwork_list,Ynetwork_list,Shortest_path_length_network_list))
my_data_el_3=my_data_el_3.T
np.savetxt(filename_el_3,my_data_el_3, delimiter=',', header='t_list,V_list,I_list,Rnetwork_list,Ynetwork_list,Shortest_path_length_network_list',comments='')



#%% ############################# - PLOTS - ###################################


### Plot 1 - NW network

if plt_network_adj_matrix:
    
    fig, ax = plt.subplots()
    fig.set_size_inches(10,10)
    plt.imshow(Adj_matrix, cmap='binary')
    plt.colorbar()
    plt.show()

    Lx = wires_dict['length_x']
    Ly = wires_dict['length_y']

if plot_network_1:
 
    # Plot pretty pictures of what we just did
    fig, ax = plt.subplots()
    fig.set_size_inches(10,10)


    ax.add_patch(Rectangle((0,0), Lx, Ly, color= (0.9,0.9,0.9), alpha=0.77))     
    ax = draw_wires(ax, wires_dict)
    ax = draw_junctions(ax, wires_dict)
    ax.set_aspect(1) # set aspect ratio to 1
    ax.set_xlabel(r'x ($\mu$m)')
    ax.set_ylabel(r'y ($\mu$m)')
    ax.ticklabel_format(style='plain', axis='x', scilimits=(0,0))
    ax.ticklabel_format(style='plain', axis='y', scilimits=(0,0))
    ax.axis([-.1*Lx,1.1*Lx,-.1*Lx,1.1*Lx]) # add some space around the unit square
    ax.set_title('Nanowires distribution')
    ax.grid()
    plt.show()
    
    
    
if plot_network_2:
 
    # Plot pretty pictures of what we just did
    fig, ax = plt.subplots()
    fig.set_size_inches(10,10)
    
    pos=nx.get_node_attributes(G,'pos')
    Lx = wires_dict['length_x']
    Ly = wires_dict['length_y']
      
    ax.set_aspect(1) # set aspect ratio to 1
    ax.set_xlabel(r'x ($\mu$m)')
    ax.set_ylabel(r'y ($\mu$m)')
    ax.ticklabel_format(style='plain', axis='x', scilimits=(0,0))
    ax.ticklabel_format(style='plain', axis='y', scilimits=(0,0))
    ax.axis([-.1*Lx,1.1*Lx,-.1*Lx,1.1*Lx]) # add some space around the unit square
    ax.set_title('Nanowires distribution graph')

    nx.draw_networkx(G,pos, node_color='r',node_size=20, with_labels=True, Hold=True)
    ax.grid()
    plt.show()



### Plot 3 - 

if plot_network_3:
    fig, ax = plt.subplots()
    fig.set_size_inches(10,10)
    ax.set_title('kamada_kawai')
    nx.draw_kamada_kawai(G, node_color='r',node_size=20, with_labels=False)
    ax.grid()
    plt.show()

    

### Plot 4 - G degree of nodes

if plot_network_4:

    degree_sequence = sorted([d for n, d in G.degree()], reverse=True)  # degree sequence
    # print "Degree sequence", degree_sequence
    degreeCount = collections.Counter(degree_sequence)
    deg, cnt = zip(*degreeCount.items())



    fig, ax = plt.subplots()
    #plt.hist(degree_sequence, bins=np.arange(min(degree_sequence), max(degree_sequence) + 1, 0.5))


    plt.bar(deg, cnt, width=0.8, color='b', align='center')
    
    plt.title("Degree Histogram")
    plt.ylabel("Count")
    plt.xlabel("Degree")
    ax.set_xticks([d for d in deg])
    ax.set_xticklabels(deg)

    plt.show()
    
    
    

##List of connected components for following graphs
list_connected_components = sorted(nx.connected_components(G),key=len, reverse=True)


if plot_network_5:
    
    # Plot pretty pictures of what we just did
    fig, ax = plt.subplots()
    fig.set_size_inches(10,10)
    
    pos=nx.get_node_attributes(G,'pos')
    Lx = wires_dict['length_x']
    Ly = wires_dict['length_y']
      
    ax.set_aspect(1) # set aspect ratio to 1
    ax.set_xlabel(r'x ($\mu$m)')
    ax.set_ylabel(r'y ($\mu$m)')
    ax.ticklabel_format(style='plain', axis='x', scilimits=(0,0))
    ax.ticklabel_format(style='plain', axis='y', scilimits=(0,0))
    ax.axis([-.1*Lx,1.1*Lx,-.1*Lx,1.1*Lx]) # add some space around the unit square
    ax.set_title('Connected components')

    n=round(len(list_connected_components)/5)+1
    colors=['g','b','c','m','y']*n
    colors.insert(0,'r')


    for i in range(0,len(list_connected_components)):
        a=[x for x in list_connected_components[i]]
        if len(a)==1:
            G.nodes[a[0]]['component_color']='k'
        else:
            for n in range(0,len(a)):
                G.nodes[a[n]]['component_color']=colors[i]



    nx.draw_networkx(G,pos, node_color=[G.nodes[u]['component_color'] for u in G.nodes()],node_size=20, with_labels=False, Hold=True)
    ax.grid()
    plt.show()
    
    
    
if plot_network_6:
 
    # Plot pretty pictures of what we just did
    fig, ax = plt.subplots()
    fig.set_size_inches(10,10)
    
    pos=nx.get_node_attributes(K,'pos')
    Lx = wires_dict['length_x']
    Ly = wires_dict['length_y']
      
    ax.set_aspect(1) # set aspect ratio to 1
    ax.set_xlabel(r'x ($\mu$m)')
    ax.set_ylabel(r'y ($\mu$m)')
    ax.ticklabel_format(style='plain', axis='x', scilimits=(0,0))
    ax.ticklabel_format(style='plain', axis='y', scilimits=(0,0))
    ax.axis([-.1*Lx,1.1*Lx,-.1*Lx,1.1*Lx]) # add some space around the unit square
    ax.set_title('Nanowires distribution graph')

    nx.draw_networkx(K,pos, node_color='r',node_size=20, with_labels=True, Hold=True)
    ax.grid()
    plt.show()
    
    
    
if plot_network_7:
    
    # Plot pretty pictures of what we just did
    fig, ax = plt.subplots()
    fig.set_size_inches(10,10)
    
    pos=nx.get_node_attributes(G,'pos')
    Lx = wires_dict['length_x']
    Ly = wires_dict['length_y']
      
    ax.set_aspect(1) # set aspect ratio to 1
    ax.set_xlabel(r'x ($\mu$m)')
    ax.set_ylabel(r'y ($\mu$m)')
    ax.ticklabel_format(style='plain', axis='x', scilimits=(0,0))
    ax.ticklabel_format(style='plain', axis='y', scilimits=(0,0))
    ax.axis([-.1*Lx,1.1*Lx,-.1*Lx,1.1*Lx]) # add some space around the unit square
    ax.set_title('Connected components')

    n=round(len(list_connected_components)/5)+1
    colors=['lightgray','lightgray','lightgray','lightgray','lightgray']*n
    colors.insert(0,'b')


    for i in range(0,len(list_connected_components)):
        a=[x for x in list_connected_components[i]]
        if len(a)==1:
            G.nodes[a[0]]['component_color']='lightgray'
        else:
            for n in range(0,len(a)):
                G.nodes[a[n]]['component_color']=colors[i]



    nx.draw_networkx(G,pos, node_color=[G.nodes[u]['component_color'] for u in G.nodes()],node_size=20, with_labels=False, Hold=True)
    
    
    
    nx.draw_networkx_nodes(G,pos,
                       nodelist=[sourcenode],
                       node_color='r',
                       node_size=300,
                   alpha=0.5)
    
    nx.draw_networkx_nodes(G,pos,
                       nodelist=[groundnode],
                       node_color='k',
                       node_size=300,
                   alpha=0.5)
    
    #ax.grid()
    plt.show()
    

    

if plot_conductance:
    
    ### Plot 6 - G-V characteristic
    fig, ax1 = plt.subplots()

    color = 'tab:red'
    ax1.set_xlabel('time (s)')
    ax1.set_ylabel('Input Voltage (V)', color=color)
    ax1.plot(t_list, V_list, color=color)
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

#%% PLOT VOLTAGE MAP
timestamp_map=0

if voltage_distribution_map:

    L=H_list[timestamp_map].copy()
    
    fig, ax = plt.subplots()
    fig.set_size_inches(10,10)
    
    pos=nx.get_node_attributes(L,'pos')
    Lx = wires_dict['length_x']
    Ly = wires_dict['length_y']
      
    ax.set_aspect(1) # set aspect ratio to 1
    ax.set_xlabel(r'x ($\mu$m)')
    ax.set_ylabel(r'y ($\mu$m)')
    ax.ticklabel_format(style='plain', axis='x', scilimits=(0,0))
    ax.ticklabel_format(style='plain', axis='y', scilimits=(0,0))
    ax.axis([-.1*Lx,1.1*Lx,-.1*Lx,1.1*Lx]) # add some space around the unit square
    ax.set_title('Nanowires distribution graph')

   
    nx.draw_networkx(L, pos, 
                 node_size=20,
                 node_color=[L.nodes[n]['V'] for n in L.nodes()],
                 cmap=plt.cm.plasma,   #viridis  #jet #Blues 
                 #edge_color=[L[u][v]['Y'] for u,v in L.edges()],
                 #width=2, 
                 #edge_cmap=plt.cm.Reds, 
                 #edge_vmin=Y_min,
                 #edge_vmax=Y_max,
                 arrows= False,
                 with_labels=False,font_size=6,
                 )
    
    nx.draw_networkx_nodes(L,pos,
                       nodelist=[mapping[sourcenode]],
                       node_color='r',
                       node_size=300,
                   alpha=0.5)
    
    nx.draw_networkx_nodes(L,pos,
                       nodelist=[mapping[groundnode]],
                       node_color='k',
                       node_size=300,
                   alpha=0.5)

    ##ax.grid()
    plt.show()
    


#%% PLOT CONDUCTANCE MAP
timestamp_map=80

if conductance_map:
    
    L=H_list[timestamp_map].copy()
    
    fig, ax = plt.subplots()
    fig.set_size_inches(10,10)
    
    pos=nx.get_node_attributes(L,'pos')
    Lx = wires_dict['length_x']
    Ly = wires_dict['length_y']
      
    ax.set_aspect(1) # set aspect ratio to 1
    ax.set_xlabel(r'x ($\mu$m)')
    ax.set_ylabel(r'y ($\mu$m)')
    ax.ticklabel_format(style='plain', axis='x', scilimits=(0,0))
    ax.ticklabel_format(style='plain', axis='y', scilimits=(0,0))
    ax.axis([-.1*Lx,1.1*Lx,-.1*Lx,1.1*Lx]) # add some space around the unit square
    ax.set_title('Nanowires distribution graph')

   
    nx.draw_networkx(L, pos, 
                 node_size=20,
                 node_color=[L.nodes[n]['V'] for n in L.nodes()],
                 cmap=plt.cm.Blues,
                 edge_color=[L[u][v]['Y'] for u,v in L.edges()],
                 width=2, 
                 edge_cmap=plt.cm.Reds, 
                 edge_vmin=Y_min,
                 edge_vmax=Y_max,
                 arrows= False,
                 with_labels=False,font_size=6,)
    
    nx.draw_networkx_nodes(L,pos,
                       nodelist=[mapping[sourcenode]],
                       node_color='r',
                       node_size=300,
                   alpha=0.5)
    
    nx.draw_networkx_nodes(L,pos,
                       nodelist=[mapping[groundnode]],
                       node_color='k',
                       node_size=300,
                   alpha=0.5)

    ##ax.grid()
    plt.show()
    
    
    
#%% INFORMATION_CENTRALITY_MAP
timestamp_map=80

if information_centrality_map:
    
    L=H_list[timestamp_map].copy()
    
    fig, ax = plt.subplots()
    fig.set_size_inches(10,10)
    
    pos=nx.get_node_attributes(L,'pos')
    Lx = wires_dict['length_x']
    Ly = wires_dict['length_y']
      
    ax.set_aspect(1) # set aspect ratio to 1
    ax.set_xlabel(r'x ($\mu$m)')
    ax.set_ylabel(r'y ($\mu$m)')
    ax.ticklabel_format(style='plain', axis='x', scilimits=(0,0))
    ax.ticklabel_format(style='plain', axis='y', scilimits=(0,0))
    ax.axis([-.1*Lx,1.1*Lx,-.1*Lx,1.1*Lx]) # add some space around the unit square
    ax.set_title('Nanowires distribution graph')


    #scaling information centrality to node sizes
    
    min_information_centrality=min([min(element) for element in Information_centrality_list])
    max_information_centrality=max([max(element) for element in Information_centrality_list])
    
    min_node_size = 0.0001
    max_node_size = 60
    
    m= (max_node_size - min_node_size )/ (max_information_centrality - min_information_centrality)
    b= max_node_size-(m*max_information_centrality)
    
    centrality_normalized=[[] for t in range(0,len(Information_centrality_list[timestamp_map]))] 
    
    for i in range(0, len(Information_centrality_list[timestamp_map])):
        centrality_normalized[i]=(m*Information_centrality_list[timestamp_map][i])+b
   
    
    
    
    nx.draw_networkx(L, pos, 
                 node_size=centrality_normalized,
                 node_color=[L.nodes[n]['information_centrality'] for n in L.nodes()],
                 cmap=plt.cm.cool,
                 edge_color=[L[u][v]['Y'] for u,v in L.edges()],
                 width=2, 
                 edge_cmap=plt.cm.Reds, 
                 edge_vmin=Y_min,
                 edge_vmax=Y_max,
                 arrows= False,
                 with_labels=False,font_size=6,)
    
    nx.draw_networkx_nodes(L,pos,
                       nodelist=[mapping[sourcenode]],
                       node_color='r',
                       node_size=300,
                   alpha=0.5)
    
    nx.draw_networkx_nodes(L,pos,
                       nodelist=[mapping[groundnode]],
                       node_color='k',
                       node_size=300,
                   alpha=0.5)

    ##ax.grid()
    plt.show()

#%% ANIMATION 1 (draw_networkx function)
if animation_1:

    ### Parameters

    frames_num = timesteps
    frames_interval=1500

    fig3, ax = plt.subplots(figsize=(10,10))


    ### Update function

    def update(i):
    
        plt.cla() 
    
        pos=nx.get_node_attributes(H_list[i],'pos')
    
    
        nx.draw_networkx(H_list[i], pos, 
                         #NODES
                         node_size=60,
                         node_color=[H_list[i].nodes[n]['V'] for n in H_list[i].nodes()],
                         cmap=plt.cm.Blues,
                         vmin=-5,
                         vmax=10,
                         #EDGES
                         width=4,
                         edge_color=[H_list[i][u][v]['Y'] for u,v in H_list[i].edges()],
                         edge_cmap=plt.cm.Reds,
                         edge_vmin=Y_min,
                         edge_vmax=Y_max,
                         with_labels=False,   #Set TRUE to see node numbers
                         font_size=6,)
    
        ax.set_title("t= {}".format(round(t_list[i], 1)))
    

    ### Animation
    anim = matplotlib.animation.FuncAnimation(fig3, update, frames= frames_num, interval=frames_interval, blit=False, repeat=True)

    anim.save('animation_1.gif', writer='imagemagick')

###############################################################################



'''
#%% ANIMATION 2 (draw_kamada_kawai)

### Parameters

frames_num = timesteps
frames_interval=1500

fig3, ax = plt.subplots(figsize=(10,10))


### Update function

def update(i):
    
    plt.cla() 
    
      
    
    nx.draw_kamada_kawai(H_list[i], 
                 #NODES
                 node_size=60,
                 node_color=[H_list[i].nodes[n]['V'] for n in H_list[i].nodes()],
                 cmap=plt.cm.Blues,
                 vmin=-5,
                 vmax=10,
                 #EDGES
                 width=4,
                 edge_color=[H_list[i][u][v]['Y'] for u,v in H_list[i].edges()],
                 edge_cmap=plt.cm.Reds,
                 edge_vmin=Y_min,
                 edge_vmax=Y_max,
                 with_labels=False,   #Set TRUE to see node numbers
                 font_size=6,)
    
    ax.set_title("t= {}".format(round(t_list[i], 1)))
    

### Animation
anim = matplotlib.animation.FuncAnimation(fig3, update, frames= frames_num, interval=frames_interval, blit=False, repeat=True)

anim.save('animation_2.gif', writer='imagemagick')

###############################################################################
'''

