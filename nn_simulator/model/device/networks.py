import networkx as nx
import numpy as np

from nn_simulator.logger import logger
from nn_simulator.model.device.datasheet.Datasheet import Datasheet
from nn_simulator.model.device.network import Network
from nn_simulator.model.device.wires import detect_junctions
from nn_simulator.model.device.wires import generate_adj_matrix
from nn_simulator.model.device.wires import generate_wires_distribution
from typing import Dict


def generate_network_data(datasheet: Datasheet) -> Dict:
    """
    Generate the data of the network according to the datasheet specifications.

    Parameters
    ----------
    datasheet: Datasheet
        the technical description of the nanowire network
    Returns
    -------
    A dictionary with the physical information about the nanowire network.
    """

    logger.info('Generating network data')

    # generate the network
    wires_dict = generate_wires_distribution(
        number_of_wires=datasheet.wires_count,
        wire_av_length=datasheet.mean_length,
        wire_dispersion=datasheet.std_length,
        general_normal_shape=10,
        centroid_dispersion=datasheet.centroid_dispersion,
        seed=datasheet.seed,
        Lx=datasheet.Lx,
        Ly=datasheet.Ly
    )

    # get junctions list and their positions
    detect_junctions(wires_dict)

    # generate graph object and adjacency matrix
    generate_adj_matrix(wires_dict)

    return wires_dict


def nn2nx(network: Network) -> nx.Graph:
    """
    Converts a nanowire network from the matrix format to a Networkx graph.

    Parameters
    ----------
    network: Network
        Matrix format of the nanowire network
    Returns
    -------
    A Networkx graph with all the information (voltage, conductance, etc.) in
    nodes and edges as fields.
    """

    graph = nx.from_numpy_matrix(network.adjacency)

    # add wire voltage to nodes
    for n in graph.nodes():
        graph.nodes[n]['V'] = float(network.voltage[n])

    # add junction tension to edge
    for u, v in graph.edges():
        graph[u][v]['V'] = float(network.voltage[u] - network.voltage[v])

    # add junction conductance and admittance to edge
    for u, v in graph.edges():
        graph[u][v]['Y'] = float(network.circuit[u, v])
        graph[u][v]['g'] = float(network.admittance[u, v])

    # add wires position to node
    xs, ys = network.wires_position
    for n in graph.nodes():
        x = xs[n, n] if n < xs.shape[0] and n < xs.shape[1] else 0
        y = ys[n, n] if n < ys.shape[0] and n < ys.shape[1] else 0
        graph.nodes[n]['pos'] = float(x), float(y)

    # add junction position to edge
    xs, ys = network.junctions_position
    for u, v in graph.edges():
        x = xs[u, v] if u < xs.shape[0] and v < xs.shape[1] else 0
        y = ys[u, v] if u < ys.shape[0] and v < ys.shape[1] else 0
        graph[u][v]['jx_pos'] = float(x), float(y)

    # add ground label to node
    for i in range(network.wires, network.nodes):
        graph.nodes[i]['ground'] = True
        if i >= network.wires + network.device_grounds:
            graph.nodes[i]['external'] = True

    return graph


def nx2nn(graph: nx.Graph) -> Network:
    """
    Converts a Networkx graph from the matrix format to a nanowire network.

    Parameters
    ----------
    graph: nx.Graph
        a Networkx graph with all the information (voltage, conductance, etc.)
        in nodes and edges as fields
    Returns
    -------
    Matrix format of the nanowire network.
    """

    adjacency = np.asarray(nx.to_numpy_array(graph), dtype=np.float32)

    # get wires position from node
    wx, wy = np.zeros_like(adjacency), np.zeros_like(adjacency)
    for n in graph.nodes():
        wx[n, n], wy[n, n] = graph.nodes[n]['pos']

    # add junction position to edge
    jx, jy = np.zeros_like(adjacency), np.zeros_like(adjacency)
    for u, v in graph.edges():
        jx[v, u], jy[v, u] = jx[u, v], jy[u, v] = graph[u][v]['jx_pos']

    # get junction conductance to edge
    circuit, admittance = np.zeros_like(adjacency), np.zeros_like(adjacency)
    for u, v in graph.edges():
        edge = graph[u][v]
        circuit[u, v] = circuit[v, u] = edge['Y'] if 'Y' in edge else 0
        admittance[u, v] = admittance[v, u] = edge['g'] if 'g' in edge else 0

    # get ground label from node
    d_grounds = sum(1 for _ in graph.nodes() if 'ground' in graph.nodes[_])
    e_grounds = sum(1 for _ in graph.nodes() if 'external' in graph.nodes[_])

    # get wire voltage to nodes and set grounds
    voltage = np.zeros(len(adjacency))
    for n in graph.nodes():
        voltage[n] = graph.nodes[n]['V'] if 'V' in graph.nodes[n] else 0

    network = Network(
        adjacency=adjacency,
        wires_position=(wx, wy),
        junctions_position=(jx, jy),
        circuit=circuit,
        admittance=admittance,
        voltage=voltage,
        device_grounds=d_grounds,
        external_grounds=e_grounds
    )

    return network


def to_np(array: np.ndarray | np.ndarray) -> np.ndarray:
    """
    Ensure that the given array is numpy one. If it's not, it is converted.

    Parameters
    ----------
    array: np.ndarray | np.ndarray
        The array that is wanted to be a numpy one
    Returns
    -------
    A numpy version of the input array.
    """

    return np.asnumpy(array) if isinstance(array, np.ndarray) else array


def to_cp(array: np.ndarray | np.ndarray) -> np.ndarray:
    """
    Ensure that the given array is cupy one. If it's not, it is converted.

    Parameters
    ----------
    array: np.ndarray | np.ndarray
        The array that is wanted to be a numpy one
    Returns
    -------
    A cupy version of the input array.
    """

    if isinstance(array, np.ndarray):
        return np.asarray(array, dtype=np.float32)
    return array
