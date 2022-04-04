# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module generates a distribution of nano-wires on 2D domain, akin to the
where atomic switch networks are grown.
The basic process consists in choosing a random center point for the wire in 
the unit square and then chooses a random angle \theta \in (0,\pi) as the
wire's orientation.

The code has been produced by:
@author: Paula Sanz-Leon <paula.sanz-leon@sydney.edu.au>
@author: Miro Astore <miro.astore@sydney.edu.au>
Included by:
@author: Gianluca Milano
And simplified/cleaned by:
@author: Paolo Baldini
"""
import numpy as np

from itertools import combinations, count as inf
from nn_simulator.logger import logger
from scipy.spatial.distance import cdist
from typing import Dict


def generate_wires_distribution(
        number_of_wires: int = 1500,
        wire_av_length: float = 14.0,
        wire_dispersion: float = 5.0,
        centroid_dispersion: float = 1200.0,
        general_normal_shape: int = 5,
        Lx: int = 3e3,
        Ly: int = 3e3,
        seed: int = 42
) -> Dict:
    """
    Drops nano-wires on the device of sides Lx, Ly. 

    Parameters
    ----------
    number_of_wires : int 
        Total number of wires to be sampled
    wire_av_length : float 
        Average wire length in mum (default = 14)
    wire_dispersion : float 
        Dispersion/scale of length distribution in mum
    centroid_dispersion : float 
        Scale parameter for the general normal distribution from 
        which centroids of wires are drawn in mum
    general_normal_shape : float 
        Shape parameter of the general normal distribution from 
        which centroids of wires are drawn. As this number increases, 
        the distribution approximates a uniform distribution.
    Lx : float 
        Horizontal length of the device in mum
    Ly : float 
        Vertical length of the device in mum
    seed : int
        Seed of the random number generator to always generate the same
        distribution

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

    # generate centroids distribution (?)
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
        np.array([xc, yc], dtype=np.float32).T,
        np.array([xc, yc], dtype=np.float32).T,
        metric='euclidean'
    )

    # Find values outside the domain
    a = np.where(np.vstack([xa, xb, ya, yb]) < 0.0, True, False).sum(axis=0)
    b = np.where(np.vstack([xa, xb]) > Lx, True, False).sum(axis=0)
    c = np.where(np.vstack([ya, yb]) > Ly, True, False).sum(axis=0)

    return dict(
        xa=xa, ya=ya,
        xc=xc, yc=yc,
        xb=xb, yb=yb,
        theta=theta,
        avg_length=wire_av_length, wire_lengths=wire_lengths,
        dispersion=wire_dispersion, centroid_dispersion=centroid_dispersion,
        gennorm_shape=general_normal_shape,
        seed=seed,
        outside=a + b + c,
        length_x=Lx, length_y=Ly,
        number_of_wires=number_of_wires,
        wire_distances=wire_distances
    )


def generate_dist_lengths(number_of_wires, wire_av_length, wire_dispersion):
    """Generates the distribution of wire lengths."""

    def positive_value(mu=wire_av_length, sigma=wire_dispersion):
        return next(x for _ in inf() if (x := np.random.normal(mu, sigma)) >= 0)
    array = [positive_value() for _ in range(number_of_wires)]
    return np.array(array, dtype=np.float32)


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
          + polish these docstring with standard input/output definitions
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
    a1 = (p0[1] - p1[1]) / (p0[0] - p1[0])  # will fail if division by zero
    a2 = (p2[1] - p3[1]) / (p2[0] - p3[0])
    b1 = p0[1] - a1 * p0[0]
    b2 = p2[1] - a2 * p2[0]

    xi = (b2 - b1) / (a1 - a2)
    yi = a1 * xi + b1

    # the last thing to do is check that xi, yi are included in interval_i:
    if (
            xi < min(interval_xi) or xi > max(interval_xi)
    ) or (
            yi < min(interval_yi) or yi > max(interval_yi)
    ):
        return False

    return xi, yi


def detect_junctions(wires_dict):
    """
    Find all the pairwise intersections of the wires contained in wires_dict.
    Adds four keys to the dictionary: junction coordinates, edge list, and
    number of junctions.

    Parameters
    ----------
    wires_dict: dict
    """

    logger.debug('Detecting junctions')
    xi, yi, edge_list = [], [], []
    for first, second in combinations(range(wires_dict['number_of_wires']), 2):

        def points(wire): return [
            [wires_dict['xa'][wire], wires_dict['ya'][wire]],
            [wires_dict['xb'][wire], wires_dict['yb'][wire]]
        ]

        p0, p1 = map(np.array, points(first))
        p2, p3 = map(np.array, points(second))

        # find and save junctions coordinates
        if junction := find_segment_intersection(p0, p1, p2, p3):
            xi.append(junction[0])
            yi.append(junction[1])

            # save node indices for every edge
            edge_list.append([first, second])

    # save centres coordinates and edge list to dict if there are junctions
    if not edge_list:
        raise Exception('There are no junctions in this network')

    wires_dict['number_of_junctions'] = len(edge_list)
    wires_dict['xi'] = np.asarray(xi, dtype=np.float32)
    wires_dict['yi'] = np.asarray(yi, dtype=np.float32)
    wires_dict['edge_list'] = np.asarray(edge_list, dtype=np.float32)

    logger.debug('Finished detecting junctions')


def generate_adj_matrix(wires_dict):
    """
    This function will produce adjacency matrix of the physical network

    Parameters
    ----------
    wires_dict: dict
        a dictionary with all the wires position and junctions/intersection 
        positions.
    """

    # create array -- maybe use sparse matrix?
    wires_count, edges = wires_dict['number_of_wires'], wires_dict['edge_list']
    adj_matrix = np.zeros((wires_count, wires_count), dtype=np.float32)
    adj_matrix[edges.astype(np.int32)[:, 0], edges.astype(np.int32)[:, 1]] = 1.0

    # make the matrix symmetric
    wires_dict['adj_matrix'] = adj_matrix + adj_matrix.T
