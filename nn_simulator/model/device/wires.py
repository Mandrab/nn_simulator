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
from typing import Dict, Any, Tuple


def generate_wires_distribution(
        number_of_wires: int = 1500,
        wire_av_length: float = 14.0,
        wire_dispersion: float = 5.0,
        centroid_dispersion: float = 1200.0,
        general_normal_shape: int = 5,
        Lx: int = 3e3,
        Ly: int = 3e3,
        seed: int = 42
) -> Dict[str, Any]:
    """
    Drops nano-wires on the device of sides Lx, Ly. 

    Parameters
    ----------
    number_of_wires: int 
        Total number of wires to be sampled
    wire_av_length: float 
        Average wire length in mum (default = 14)
    wire_dispersion: float 
        Dispersion/scale of length distribution in mum
    centroid_dispersion: float 
        Scale parameter for the general normal distribution from 
        which centroids of wires are drawn in mum
    general_normal_shape: float 
        Shape parameter of the general normal distribution from 
        which centroids of wires are drawn. As this number increases, 
        the distribution approximates a uniform distribution.
    Lx: float 
        Horizontal length of the device in mum
    Ly: float 
        Vertical length of the device in mum
    seed: int
        Seed of the random number generator to always generate the same
        distribution

    Returns
    -------
    A dictionary with the centre coordinates, the end point coordinates, and
    orientations. The `outside` key in the dictionary is 1 when
    the wire intersects an edge of the device and is 0 otherwise.
    """

    np.random.seed(seed)

    # wire lengths distribution
    wire_lengths = generate_dist_lengths(
        number_of_wires, wire_av_length, wire_dispersion
    )

    # generate wire centroids distribution
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


def generate_dist_lengths(
        number_of_wires: int,
        wire_av_length: float,
        wire_dispersion: float
) -> np.ndarray:
    """
    Generates the distribution of wire lengths.

    Parameters
    ----------
    number_of_wires: int
        In the device
    wire_av_length: float
        Average length of a wire
    wire_dispersion: float
        In the device

    Returns
    -------
    A numpy ndarray of the distribution.
    """

    def positive_value(mu=wire_av_length, sigma=wire_dispersion):
        return next(x for _ in inf() if (x := np.random.normal(mu, sigma)) >= 0)
    array = [positive_value() for _ in range(number_of_wires)]
    return np.array(array, dtype=np.float32)


def generate_dist_orientations(number_of_wires) -> np.ndarray:
    # uniform random angle in [0,pi)
    return np.random.rand(int(number_of_wires)) * np.pi


def detect_junctions(wires_dict: Dict[str, Any]):
    """
    Find all the pairwise intersections of the wires contained in wires_dict.
    Adds four keys to the dictionary: junction coordinates, edge list, and
    number of junctions.

    Parameters
    ----------
    wires_dict: Dict[str, Any]
        The wires distribution container
    """

    logger.debug('Detecting junctions')

    xa, ya = wires_dict['xa'], wires_dict['ya']
    xb, yb = wires_dict['xb'], wires_dict['yb']

    # calculate distance between start and end point
    delta_x, delta_y = xa - xb, ya - yb
    x_ranges = [(min(_), max(_)) for _ in zip(xa, xb)]
    y_ranges = [(min(_), max(_)) for _ in zip(ya, yb)]

    m = xa * yb - ya * xb

    def junction(first: int, second: int) -> bool | Tuple[float, float]:
        c = delta_x[first] * delta_y[second] - delta_y[first] * delta_x[second]

        # no intersection
        if abs(c) < 0.01:
            return False

        a, b = m[first], m[second]

        x = (a * delta_x[second] - b * delta_x[first]) / c
        y = (a * delta_y[second] - b * delta_y[first]) / c

        def between(value: float, min_: float, max_: float) -> bool:
            return min_ <= value <= max_

        # exclude junction points out of the points area
        if not (
            between(x, *x_ranges[first]) and between(x, *x_ranges[second])
        ) or not (
            between(y, *y_ranges[first]) and between(y, *y_ranges[second])
        ):
            return False

        return x, y

    wires_count = range(wires_dict['number_of_wires'])
    junctions = [(_, junction(*_)) for _ in combinations(wires_count, 2)]
    junctions = dict(filter(lambda _: _[1], junctions))

    xj = np.array([*map(lambda _: _[0], junctions.values())], dtype=np.float32)
    yj = np.array([*map(lambda _: _[0], junctions.values())], dtype=np.float32)
    edge_list = np.array([*junctions.keys()], dtype=np.float32)

    if not edge_list.size:
        raise Exception('There are no junctions in this network')

    wires_dict['number_of_junctions'] = len(edge_list)
    wires_dict['xi'] = xj
    wires_dict['yi'] = yj
    wires_dict['edge_list'] = edge_list

    logger.debug('Finished detecting junctions')


def generate_adj_matrix(wires_dict):
    """
    This function will produce adjacency matrix of the physical network.

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
