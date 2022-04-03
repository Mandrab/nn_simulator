import cupy as cp
import networkx as nx
import numpy as np

from .datasheet.Datasheet import Datasheet
from .wires import generate_wires_distribution, detect_junctions
from .wires import generate_adj_matrix
from nanowire_network_simulator.model.device.network import Network
from nanowire_network_simulator.logger import logger
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
    A dictionary with the physical information about the nanowire network
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
    nodes and edges as fields
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
        graph.nodes[n]['pos'] = tuple(map(float, (xs[n, n], ys[n, n])))

    # add junction position to edge
    xs, ys = network.junctions_position
    for u, v in graph.edges():
        graph[u][v]['jx_pos'] = tuple(map(float, (xs[u, v], ys[u, v])))

    # add ground label to node
    for i in range(network.grounds):
        graph.nodes[i]['ground'] = True

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
    Matrix format of the nanowire network
    """

    adjacency = cp.asarray(nx.to_numpy_array(graph), dtype=cp.float32)

    # get wires position from node
    wx, wy = cp.zeros_like(adjacency), cp.zeros_like(adjacency)
    for n in graph.nodes():
        wx[n, n], wy[n, n] = graph.nodes[n]['pos']

    # add junction position to edge
    jx, jy = cp.zeros_like(adjacency), cp.zeros_like(adjacency)
    for u, v in graph.edges():
        jx[v, u], jy[v, u] = jx[u, v], jy[u, v] = graph[u][v]['jx_pos']

    # get junction conductance to edge
    circuit, admittance = cp.zeros_like(adjacency), cp.zeros_like(adjacency)
    for u, v in graph.edges():
        edge = graph[u][v]
        circuit[u, v] = circuit[v, u] = edge['Y'] if 'Y' in edge else 0
        admittance[u, v] = admittance[v, u] = edge['g'] if 'g' in edge else 0

    # get ground label from node
    grounds = sum(1 for _ in graph.nodes() if 'ground' in graph.nodes[_])

    # get wire voltage to nodes and set grounds
    voltage = cp.zeros(len(adjacency) - grounds)
    for n in graph.nodes():
        voltage[n] = graph.nodes[n]['V'] if 'V' in graph.nodes[n] else 0

    network = Network(
        adjacency=adjacency,
        wires_position=(wx, wy),
        junctions_position=(jx, jy),
        circuit=circuit,
        admittance=admittance,
        voltage=voltage,
        grounds=grounds
    )

    return network


def to_np(array: np.ndarray | cp.ndarray) -> np.ndarray:
    return cp.asnumpy(array) if isinstance(array, cp.ndarray) else array


def to_cp(array: np.ndarray | cp.ndarray) -> cp.ndarray:
    if isinstance(array, np.ndarray):
        return cp.asarray(array, dtype=cp.float32)
    return array
