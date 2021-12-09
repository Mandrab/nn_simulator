# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module generates a distribution of nano-wires on 2D domain, akin to the
where atomic switch networks are grown. 
The basic process consists in choosing a random center point for the wire in 
the unit square and then chooses a random angle \theta \in (0,\pi) as the
wire's orientation.
@author: Paula Sanz-Leon <paula.sanz-leon@sydney.edu.au>
@author: Miro Astore <miro.astore@sydney.edu.au>

@author: milan
"""

import logging
import networkx as nx
import numpy as np

from itertools import combinations
from scipy.spatial.distance import cdist


def generate_wires_distribution(
        number_of_wires: int = 1500,
        wire_av_length: float = 14.0,
        wire_dispersion: float = 5.0,
        centroid_dispersion: float = 1200.0,
        general_normal_shape: int = 5,
        Lx: int = 3e3,
        Ly: int = 3e3,
        seed: int = 42
) -> dict:
    """
    Drops nano-wires on the device of sides Lx, Ly. 

    Parameters
    ----------
    number_of_wires : int 
        Total number of wires to be sampled
    wire_av_length : float 
        Average wire length in mum
    wire_dispersion : float 
        Dispersion/scale of length distribution in mum
    wire_length : float 
        Length of the nanowire in mum (default = 14)
    centroid_dispersion : float 
        Scale parameter for the general normal distribution from 
        which centroids of wires are drawn in mum
    general_normal_shape : float 
        Shape parameter of the general normal distribution from 
        which centroids of wires are drawn. As this number increases, 
        the distribution approximates a uniform distribution.
    Lx : float 
        Horizontal legth of the device in mum
    Ly : float 
        Vertical length of the device in mum
    seed : int
        Seed of the random number generator to always generate the same distribution
    
    Returns
    -------
    dict
        A dictionary with the centre coordinates, the end point coordinates, and
        orientations. The `outside` key in the dictionary is 1 when
        the wire intersects an edge of the device and is 0 otherwise.
    """

    np.random.seed(seed)

    # wire lengths
    wire_lengths = generate_dist_lengths(
        number_of_wires, wire_av_length,
        wire_dispersion
    )

    # xc, yc = generate_dist_centroids(
    #     number_of_wires, loc = Lx/2,
    #     scale = centroid_dispersion,
    #     beta = general_normal_shape
    # )
    xc = np.random.rand(number_of_wires) * Lx
    yc = np.random.rand(number_of_wires) * Ly
    theta = generate_dist_orientations(number_of_wires)

    # coordinates for one end
    xa = xc - wire_lengths / 2.0 * np.cos(theta)
    ya = yc - wire_lengths / 2.0 * np.sin(theta)

    # coordinates for the other end
    xb = xc + wire_lengths / 2.0 * np.cos(theta)
    yb = yc + wire_lengths / 2.0 * np.sin(theta)

    # Compute the Euclidean distance between pair of region centres
    wire_distances = cdist(
        np.array([xc, yc]).T,
        np.array([xc, yc]).T,
        metric='euclidean'
    )

    # Find values outside the domain
    a = np.where(np.vstack([xa, xb, ya, yb]) < 0.0, True, False).sum(axis=0)
    b = np.where(np.vstack([xa, xb]) > Lx, True, False).sum(axis=0)
    c = np.where(np.vstack([ya, yb]) > Ly, True, False).sum(axis=0)

    outside = a + b + c

    return dict(
        xa=xa, ya=ya,
        xc=xc, yc=yc,
        xb=xb, yb=yb,
        theta=theta,
        avg_length=wire_av_length,
        wire_lengths=wire_lengths,
        dispersion=wire_dispersion,
        centroid_dispersion=centroid_dispersion,
        gennorm_shape=general_normal_shape,
        seed=seed,
        outside=outside,
        length_x=Lx,
        length_y=Ly,
        number_of_wires=number_of_wires,
        wire_distances=wire_distances
    )


def generate_dist_lengths(number_of_wires, wire_av_length, wire_dispersion):
    """
    Generates the distribution of wire lengths
    """

    mu = wire_av_length
    sigma = wire_dispersion

    wire_lengths = np.random.normal(mu, sigma, int(number_of_wires))

    for i in range(len(wire_lengths)):
        while wire_lengths[i] < 0:
            wire_lengths[i] = np.random.normal(mu, sigma, 1)

    """
    gamma_shape = (wire_av_length / wire_dispersion)**2
    gamma_scale = wire_dispersion**2 / wire_av_length
    wire_lengths = np.random.gamma(gamma_shape, gamma_scale, int(number_of_wires))
    """
    return wire_lengths


def generate_dist_centroids(number_of_wires: int, loc, scale, beta=5):
    """
    Generates the 2D coordinates from a general normal distribution
    """

    # uniform random in [0,Lx) for each coordinate dimension
    xc = np.random.rand(number_of_wires) * 3000

    # uniform random in [0,Lx) for each coordinate dimension
    yc = np.random.rand(number_of_wires) * 3000

    # this is a normal distribution
    # xc = gennorm.rvs(beta, loc=loc, scale=scale, size=number_of_wires)
    # yc = gennorm.rvs(beta, loc=loc, scale=scale, size=number_of_wires)

    return xc, yc


def generate_dist_orientations(number_of_wires):
    # uniform random angle in [0,pi)
    return np.random.rand(int(number_of_wires)) * np.pi


def find_segment_intersection(p0, p1, p2, p3):
    """
    Find *line segments* intersection using line equations and 
    some boundary conditions.
    First segment is defined between p0, p1 and 
    second segment is defined between p2, p3
          p2
          |  
    p0 ------- p1
          |
          p3

    Parameters
    ----------
    p0 : array
        x, y coordinates of first wire's start point 
    p1 : array
        x, y coordinates of first wire's end point
    p2 : array
        x, y coordinates of second wire's start point 
    p3 : array
        x, y coordinates of second wire's end point
    Returns
    -------
    xi, yi: float 
       x, y coordinates of the intersection
    TODO: + change input to a list instead of individual points; or,
          + make point a class with x, y coordinates so we avoid using 
          indexing (x: pX[0]; y:pX[1])
          + polish these docstring with standard input/ouput definitions
    """

    # Check that points are not the same
    if np.array_equal(p0, p1) or np.array_equal(p2, p3):
        return False

    # Check that an overlapping interval exists
    if (
            max(p0[0], p1[0]) < min(p2[0], p3[0])
    ) or (
            max(p2[0], p3[0]) < min(p0[0], p1[0])
    ):
        return False

    # xi, yi have to be included in
    interval_xi = [
        max(min(p0[0], p1[0]), min(p2[0], p3[0])),
        min(max(p0[0], p1[0]), max(p2[0], p3[0]))
    ]
    interval_yi = [
        max(min(p0[1], p1[1]), min(p2[1], p3[1])),
        min(max(p0[1], p1[1]), max(p2[1], p3[1]))
    ]

    # Find the intersection point between nano-wires
    A1 = (p0[1] - p1[1]) / (p0[0] - p1[0])  # will fail if division by zero
    A2 = (p2[1] - p3[1]) / (p2[0] - p3[0])
    b1 = p0[1] - A1 * p0[0]
    b2 = p2[1] - A2 * p2[0]

    xi = (b2 - b1) / (A1 - A2)
    yi = A1 * xi + b1

    # the last thing to do is check that xi, yi are included in interval_i:
    if (
            xi < min(interval_xi) or xi > max(interval_xi)
    ) or (
            yi < min(interval_yi) or yi > max(interval_yi)
    ):
        return False

    return xi, yi


def select_largest_component(wires_dict):
    """
    Find and select largest connected component of the original graph G.
    Throws away unconnected components and updates all the keys in wires_dict 
    """

    wires_dict['G'] = max(
        nx.connected_component_subgraphs(wires_dict['G']),
        key=len
    )
    nw = len(wires_dict['G'].nodes())
    nj = len(wires_dict['G'].edges())

    logging.debug("The largest component has %5d nodes and %6d edges", nw, nj)

    # replace values in the dictionary
    wires_dict['number_of_wires'] = nw
    wires_dict['number_of_junctions'] = nj
    wires_dict['xa'] = wires_dict['xa'][wires_dict['G'].nodes()]
    wires_dict['ya'] = wires_dict['ya'][wires_dict['G'].nodes()]
    wires_dict['xb'] = wires_dict['xb'][wires_dict['G'].nodes()]
    wires_dict['yb'] = wires_dict['yb'][wires_dict['G'].nodes()]
    wires_dict['xc'] = wires_dict['xc'][wires_dict['G'].nodes()]
    wires_dict['yc'] = wires_dict['yc'][wires_dict['G'].nodes()]

    # keep old edge_list
    old_edge_list = [
        (ii, kk) for ii, kk in zip(
            wires_dict['edge_list'][:, 0],
            wires_dict['edge_list'][:, 1]
        )
    ]

    # remove old edge list
    wires_dict = remove_key(wires_dict, 'edge_list')

    # save indices of intersections in the old graph
    ind_dict = {key: value for value, key in enumerate(old_edge_list)}
    new_edge_list = sorted(
        [
            kk if kk[0] < kk[1]
            else (kk[1], kk[0])
            for kk in wires_dict['G'].edges()
        ],
        key=lambda x: x[0]
    )
    # find intersection between the two sets
    inter = set(ind_dict).intersection(new_edge_list)
    # retrieve edge indices/positions from the old list
    edges_idx = [ind_dict[idx] for idx in inter]

    # these have length equal to number of junctions - only get the ones we need
    wires_dict['xi'] = wires_dict['xi'][edges_idx]
    wires_dict['yi'] = wires_dict['yi'][edges_idx]

    # get contiguous numbering of nodes
    # build node mapping
    node_mapping = {
        key: value
        for value, key in enumerate(sorted(wires_dict['G'].nodes()))
    }
    # this step also renames edges list
    wires_dict['G'] = nx.relabel_nodes(wires_dict['G'], node_mapping)

    # swap node vertices if vertex 0 is larger than vertex 1,
    # then sort by first element
    wires_dict['edge_list'] = np.asarray(sorted(
        [
            kk if kk[0] < kk[1]
            else (kk[1], kk[0])
            for kk in wires_dict['G'].edges()
        ],
        key=lambda x: x[0]
    ))

    # save adjacency matrix of new graph
    wires_dict = remove_key(wires_dict, 'adj_matrix')
    wires_dict = generate_adj_matrix(wires_dict)

    wire_distances = cdist(
        np.array([wires_dict['xc'], wires_dict['yc']]).T,
        np.array([wires_dict['xc'], wires_dict['yc']]).T,
        metric='euclidean'
    )
    wires_dict['wire_distances'] = wire_distances

    return wires_dict


def detect_junctions(wires_dict):
    """
    Find all the pairwise intersections of the wires contained in wires_dict.
    Adds four keys to the dictionary: junction coordinates, edge list, and
    number of junctions.

    Parameters
    ----------
    wires_dict: dict
    Returns
    -------
    wires_dict: dict 
        with added keys
    """
    logging.debug('Detecting junctions')
    xi, yi, edge_list = [], [], []
    for first, second in combinations(range(wires_dict['number_of_wires']), 2):

        def points(wire): return (
            wires_dict['xa'][wire], wires_dict['ya'][wire],
            wires_dict['xb'][wire], wires_dict['yb'][wire]
        )

        xa, ya, xb, yb = points(first)
        p0, p1 = np.array([xa, ya]), np.array([xb, yb])

        xa, ya, xb, yb = points(second)
        p2, p3 = np.array([xa, ya]), np.array([xb, yb])

        # find junctions
        J = find_segment_intersection(p0, p1, p2, p3)

        if J is not False:

            # save coordinates
            xi.append(J[0])
            yi.append(J[1])

            # save node indices for every edge
            edge_list.append([first, second])

    # save centres coordinates and edge list to dict
    # if there are junctions
    if len(edge_list) is not 0:

        wires_dict['number_of_junctions'] = len(edge_list)
        wires_dict['xi'] = np.asarray(xi)
        wires_dict['yi'] = np.asarray(yi)
        wires_dict['edge_list'] = np.asarray(edge_list)

        logging.debug('Finished detecting junctions')

        return wires_dict

    raise Exception('There are no junctions in this network')


def generate_adj_matrix(wires_dict):
    """
    This function will produce adjacency matrix of the physical network

    Parameters
    ----------
    wires_dict: dict
        a dictionary with all the wires position and junctions/intersection 
        positions.
    Returns
    ------- 
    wires_dict: dict
        The same dictionary with added key:value pairs adjacency matrix 
    """

    # create array -- maybe use sparse matrix?
    adj_matrix_shape = (
        wires_dict['number_of_wires'], wires_dict['number_of_wires']
    )
    adj_matrix = np.zeros(adj_matrix_shape, dtype=np.float32)
    adj_matrix[
        wires_dict['edge_list'].astype(np.int32)[:, 0],
        wires_dict['edge_list'].astype(np.int32)[:, 1]
    ] = 1.0

    # make the matrix symmetric
    adj_matrix = adj_matrix + adj_matrix.T

    wires_dict['adj_matrix'] = adj_matrix

    return wires_dict


def generate_graph(wires_dict):
    """
    This function will produce a networkx graph.

    Parameters
    ----------
    wires_dict: dict
        a dictionary with all the wires position and junctions/intersection 
        positions.
    Returns
    ------- 
    wires_dict: dict
        The same dictionary with added key:value pairs networkx graph object.
    """

    # Create graph - this is going to be a memory pig for large matrices
    wires_dict = generate_adj_matrix(wires_dict)
    graph = nx.from_numpy_matrix(np.matrix(wires_dict['adj_matrix']))

    wires_dict['G'] = graph

    return wires_dict


def check_connectedness(wires_dict):
    """
    This function will check is the graph is connected.
    If it is not connected:
    (1) add new junctions 
    (2) update centre coordinates and orientation of one of the nano-wires
    (3) something else I haven't thought of yet ...
    """

    graph = wires_dict['G']

    if not nx.is_connected(graph):
        nc = nx.number_connected_components(graph)

        logging.warning("This graph has %4d connected components", nc)

        return False

    return True


def remove_key(wires_dict, key='G'):
    """
    This removes a key:value pair of the dict without 
    altering the original dictionary
    """

    temp_dict = dict(wires_dict)
    del temp_dict[key]
    return temp_dict


def reconnect_graph(
        wires_dict,
        scale_num_wires,
        scale_dispersion,
        scale_length,
        falloff_ind_wires=1.5,
        falloff_ind_length=1.5,
        falloff_ind_disp=1.5,
        distro='gamma',
        max_loop=10
):
    """
        reconnect graph by increasing length by a set factor each iteration
        more work probably needed such that length and density does not get out
        of hand.
    """

    distros = {'gamma': 1, 'uniform': 2}

    length_x = wires_dict['length_x']
    length_y = wires_dict['length_x']
    seed = wires_dict['seed']

    for i in range(max_loop):

        if check_connectedness(wires_dict):
            return wires_dict

        number_of_wires = wires_dict['number_of_wires'] * scale_num_wires
        avg_length = wires_dict['avg_length'] * scale_length
        dispersion = wires_dict['dispersion'] * scale_dispersion

        if distros[distro] == 1:
            wires_dict = generate_wires_distribution(
                number_of_wires,
                avg_length,
                dispersion,
                length_x,
                length_y,
                seed
            )

        wires_dict = detect_junctions(wires_dict)
        wires_dict = generate_graph(wires_dict)
        scale_num_wires = scale_num_wires ** falloff_ind_wires
        scale_length = scale_length ** falloff_ind_length
        scale_dispersion = scale_dispersion ** falloff_ind_disp

    return wires_dict
