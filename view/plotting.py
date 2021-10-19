#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 27 15:09:29 2019

@author: Gianluca
"""

import os
import math
import random
import networkx as nx
from networkx import grid_graph
import collections
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle




###############################################################################

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
        line = [Line2D([xa[this_wire],xb[this_wire]],[ya[this_wire],yb[this_wire]], color = (0.42, 0.42, 0.42)),
                Line2D([xc[this_wire]],[yc[this_wire]], color = 'r', marker = 'o', ms = 2, alpha = 0.77)] 
        
        '''
        if wires_dict['outside'][this_wire]:
            line = [Line2D([xa[this_wire],xb[this_wire]],[ya[this_wire],yb[this_wire]], color = 'k', ls = '--', alpha = 0.2)] 
                   #Line2D([xc[this_wire]],[yc[this_wire]],  color = 'k', marker = 'o', ms = 4, alpha = 0.1)] 
        else:   
            line = [Line2D([xa[this_wire],xb[this_wire]],[ya[this_wire],yb[this_wire]], color = (0.42, 0.42, 0.42)),
                    Line2D([xc[this_wire]],[yc[this_wire]], color = 'r', marker = 'o', ms = 2, alpha = 0.77)] 
        '''
        for l in line: 
            ax.add_line(l)

    return ax

###############################################################################

def draw_junctions(ax, wires_dict):
    """
    Draw the circles at the junctions
    """

    xi, yi = wires_dict['xi'], wires_dict['yi']

    for this_junction in range(wires_dict['number_of_junctions']):
        line = [Line2D([xi[this_junction]],[yi[this_junction]], color = 'b', marker = 'o', ms = 1.5, alpha = 0.77)]
        for l in line: 
            ax.add_line(l)
    return ax


###############################################################################


def plot_0(H):
    
    pos = nx.get_node_attributes(H,'pos')
            
    plt.figure
    
    
    node_colors = [[] for x in range(0,H.number_of_nodes())]
    '''
    for n in H.nodes():
        node_colors[n] = 'r'
        if H.nodes[n]['pad'] == True:
            node_colors[n] = 'y'
        if H.nodes[n]['source_node'] == True:
            node_colors[n] = 'm'
        if H.nodes[n]['ground_node'] == True:
            node_colors[n] = 'k'
    '''
    
    nx.draw_networkx(H, pos,node_color = node_colors, node_size = 60, with_labels = True)
    
    '''
    nx.draw_networkx_edges(H, pos, edgelist = filament_edges, edge_color = 'r', width = 10)
    '''


#####    -    PLOT_1   -  Graph with node numbers and edge conductance  #######

def plot_1(H):
    
    pos = nx.get_node_attributes(H,'pos')
    Y = nx.get_edge_attributes(H,'Y')
            
    filament_edges = [(u,v) for u,v,e in H.edges(data = True) if e['Filament'] == 1]        
    
    
    
    #plot with labels
    plt.figure
    
    nx.draw_networkx(H, pos)
    nx.draw_networkx_edge_labels(H,pos,edge_labels = Y, font_size = 6)
    nx.draw_networkx_edges(H, pos, edgelist = filament_edges, edge_color = 'r', width = 10)




##    -    PLOT_2   -  Graph with voltage node labels and edge conductance ####

def plot_2(H):
    
    pos = nx.get_node_attributes(H,'pos')
    Y = nx.get_edge_attributes(H,'Y')
    for n in H.nodes():                                                             #rounded Voltage
        H.node[n]['Vrounded'] = round(H.node[n]['V'],2)
        
    Vlabel = nx.get_node_attributes(H,'Vrounded')
    
    
    node_colors_2 = [[] for x in range(0,H.number_of_nodes())]      

    filament_edges = [(u,v) for u,v,e in H.edges(data = True) if e['Filament'] == 1]                   #add color to nodes

    '''
    sourcenode = [x for x,y in H.nodes(data = True) if y['source_node'] == True]
    '''
    for n in H.nodes():
        node_colors_2[n] = 'r'
        if H.nodes[n]['source_node'] == True:
            node_colors_2[n] = 'g'
        if n == 0:
            node_colors_2[n] = 'y'


    #plot with labels
    plt.figure
    
    nx.draw_networkx(H,pos,labels = Vlabel, font_size = 8, node_color = node_colors_2)
    nx.draw_networkx_edge_labels(H,pos,edge_labels = Y, font_size = 6)
    nx.draw_networkx_edges(H, pos, edgelist = filament_edges, edge_color = 'r', width = 10)



#####    -    PLOT_3   -  Graph with voltage node labels and current    #######

def plot_3(H):
    
    pos = nx.get_node_attributes(H,'pos')
    for n in H.nodes():                                                             #rounded Voltage
        H.node[n]['Vrounded'] = round(H.node[n]['V'],2)
        
    Vlabel = nx.get_node_attributes(H,'Vrounded')
    Ilabel = nx.get_edge_attributes(H,'Irounded')
    
    node_colors_2 = [[] for x in range(0,H.number_of_nodes())]                        #add color to nodes

    '''
    sourcenode = [x for x,y in H.nodes(data = True) if y['source_node'] == True]
    '''
    for n in H.nodes():
        node_colors_2[n] = 'r'
        if H.nodes[n]['source_node'] == True:
            node_colors_2[n] = 'g'
        if n == 0:
            node_colors_2[n] = 'y'


    #plot with labels
    plt.figure
    
    nx.draw_networkx(H,pos,labels = Vlabel, font_size = 8, node_color = node_colors_2)
    nx.draw_networkx_edge_labels(H,pos,edge_labels = Ilabel)
    
    
    
    
    
    
#####    -    PLOT_4   -  Graph with voltage node labels and current and colors#######
    
def plot_4(H):
    
    pos = nx.get_node_attributes(H,'pos')
    
    for n in H.nodes():                                                             #rounded Voltage
        H.node[n]['Vrounded'] = round(H.node[n]['V'],2)
        
    Vlabel = nx.get_node_attributes(H,'Vrounded')
    Ilabel = nx.get_edge_attributes(H,'Irounded')
    
    
    #plot with labels
    plt.figure

    nx.draw_networkx(H, pos, 
                 node_color = [H.nodes[n]['V'] for n in H.nodes()],
                 cmap = plt.cm.Blues,
                 edge_color = [H[u][v]['I'] for u,v in H.edges()],
                 edge_labels = Ilabel,
                 width = 4, edge_cmap = plt.cm.Reds, 
                 with_labels = True,labels = Vlabel,font_size = 6,)

    nx.draw_networkx_edge_labels(H,pos,edge_labels = Ilabel,font_size = 6)
    
    
    
    
    
#####    -    PLOT_5   -  As plot 4 but without node and edge labels#######
    
def plot_5(H):
    
    pos = nx.get_node_attributes(H,'pos')

    
    #plot with labels
    plt.figure

    nx.draw_networkx(H, pos, 
                 node_size = 60,
                 node_color = [H.nodes[n]['V'] for n in H.nodes()],
                 cmap = plt.cm.Blues,
                 edge_color = [H[u][v]['I'] for u,v in H.edges()],
                 width = 4, edge_cmap = plt.cm.Reds, 
                 with_labels = False,font_size = 6,)

