import cupy as cp
import numpy as np

from scipy.sparse.csgraph import connected_components
from nanowire_network_simulator.model.device.network import Network
from typing import Dict, Any, List, Tuple


def nanowire_network(
        network_data: Dict[str, Any],
        initial_conductance: float,
        grounds: int = 0
) -> Network:
    """
    Generate a nanowire network according to a dictionary (a.k.a., wires_dict)
    description.

    Parameters
    ----------
    network_data: Dict[str, any]
        the dictionary description of the network
    initial_conductance: float
        the float value to set as conductance
    grounds: int
        number of network nodes to be considered grounds. They are the rightmost
        and bottommost ones of the resulting matrix
    Returns
    -------
    A Network instance of the largest connected component
    """

    # get largest connected component of the network
    graph, mask = largest_connected_component(network_data['adj_matrix'])

    # create a matrix to store x and y positions of a wire
    wx, wy = tuple(cp.zeros_like(network_data['adj_matrix']) for _ in range(2))
    for matrix, _ in zip((wx, wy), ('xc', 'yc')):
        cp.fill_diagonal(matrix, network_data[_])

    # reduce the matrix to the largest component one
    wx, wy = [clear_matrix(_, mask) for _ in (wx, wy)]

    # create a matrix to store x and y positions of a wires junction
    adj = np.matrix.flatten(np.triu(network_data['adj_matrix']))

    # set the junctions position
    jx, jy = [cp.reshape(
        cp.asarray([
            next(_0)
            if _1 != 0 else 0
            for _1 in adj
        ], dtype=cp.float32),
        network_data['adj_matrix'].shape
    ) for _0 in [
        iter(network_data[k]) for k in ('xi', 'yi')
    ]]

    # mirror upper-diagonal of the matrix below
    jx, jy = jx + jx.T - np.diag(np.diag(jx)), jy + jy.T - np.diag(np.diag(jy))

    # reduce the matrix to the largest component one
    jx, jy = [clear_matrix(_, mask) for _ in (jx, jy)]

    # set the initial conductance of the system on non-zero junctions
    circuit = initial_conductance * (graph != 0)

    # save adjacency matrix of reduced network
    return Network(
        adjacency=cp.asarray(graph, dtype=cp.float32),
        wires_position=(wx, wy),
        junctions_position=(jx, jy),
        circuit=cp.asarray(circuit, dtype=cp.float32),
        admittance=cp.zeros_like(circuit),
        voltage=cp.zeros(len(circuit)),
        device_grounds=grounds
    )


def largest_connected_component(
        graph: np.ndarray
) -> Tuple[np.ndarray, List[bool]]:
    """
    Extract the largest connected component from the matrix.

    Parameters
    ----------
    graph: np.ndarray
        the adjacency matrix that represents the network
    Returns
    -------
    The matrix of the largest connected component
    The mask of the removed nodes
    """

    # get list of nodes membership in the graph
    _, labels = connected_components(cp.asnumpy(graph), directed=False)

    # count nodes of each component
    unique_labels, count = np.unique(labels, return_counts=True)

    # get largest connected component label
    _, label = max(zip(count, unique_labels))

    # get not connected nodes and delete their column and row from the matrix
    mask = [k != label for k in labels]
    return clear_matrix(graph, mask), mask


def clear_matrix(matrix: np.ndarray, mask: List[int]) -> cp.ndarray:
    """
    Clear a matrix removing the nodes (i.e., columns and rows) specified by the
    mask.

    Parameters
    ----------
    matrix: np.ndarray
        the matrix to clean
    mask: cp.ndarray
        the boolean mask that specify the elements to remove. A value of true
        means a removal
    Returns
    -------
    A cp.ndarray cleaned by all the exceeding nodes
    """

    matrix = np.delete(cp.asnumpy(matrix), mask, 0)
    matrix = np.delete(matrix, mask, 1)
    return cp.asarray(matrix, dtype=cp.float32)
