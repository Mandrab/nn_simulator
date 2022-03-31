import cupy as cp
import numpy as np

from dataclasses import dataclass
from scipy.sparse.csgraph import connected_components
from typing import Tuple, Dict, Any, List


@dataclass
class Network:
    """
    Contains the state of the nanowire network.

    Fields
    ------
    adjacency: cp.ndarray
        adjacency (i.e., connections) matrix of the device
    wires_position: Tuple[cp.ndarray, cp.ndarray]
        x and y position of the wires
    junctions_position: Tuple[cp.ndarray, cp.ndarray]
        x and y position of the wires junctions
    circuit: cp.ndarray
        adjacency matrix with conductances instead of 1s
    admittance: cp.ndarray
        admittance matrix for the junction resistance update
    voltage: cp.ndarray
        voltages of the circuit nodes
    ground_count: int
        specify the number of nodes to be considered ground (those have to be at
        the rightmost part of the matrix)
    """

    adjacency: cp.ndarray
    wires_position: Tuple[cp.ndarray, cp.ndarray]
    junctions_position: Tuple[cp.ndarray, cp.ndarray]

    circuit: cp.ndarray
    admittance: cp.ndarray
    voltage: cp.ndarray

    ground_count: int = 0


def nanowire_network(
        network_data: Dict[str, Any],
        initial_conductance: float,
        ground_count: int = 0
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
    ground_count: int
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
    jx, jy = [cp.reshape(
        cp.asarray([
            next(iter(network_data[_0]))
            if _1 != 0 else 0
            for _1 in adj
        ]),
        network_data['adj_matrix'].shape
    ) for _0 in ('xi', 'yi')]

    # reduce the matrix to the largest component one
    jx, jy = [clear_matrix(_, mask) for _ in (jx, jy)]

    # set the initial conductance of the system
    circuit = cp.asarray([
        [initial_conductance if _ else 0 for _ in row] for row in graph
    ])

    # save adjacency matrix of reduced network
    return Network(
        adjacency=cp.asarray(graph),
        wires_position=(wx, wy),
        junctions_position=(jx, jy),
        circuit=circuit,
        admittance=cp.zeros_like(circuit),
        voltage=cp.zeros(len(circuit)),
        ground_count=ground_count
    )


def copy(network: Network) -> Network:
    """
    Makes a deep copy of the nanowire network.

    Parameters
    ----------
    network: Network
        the network to copy
    Returns
    -------
    A copy of the input nanowire network
    """
    xw, yw = network.wires_position
    xj, yj = network.junctions_position

    return Network(
        adjacency=network.adjacency.copy(),
        wires_position=(xw.copy(), yw.copy()),
        junctions_position=(xj.copy(), yj.copy()),
        circuit=network.circuit.copy(),
        admittance=network.admittance.copy(),
        voltage=network.voltage.copy(),
        ground_count=network.ground_count
    )


def connect(network: Network, wire_idx: int, resistance: float):
    """
    Connect an external load to the network.

    Parameters
    ----------
    network: Network
        the nanowire network to connect the load to
    wire_idx: int
        index of the connection node of the nanowire network
    resistance: float
        resistance of the attached load
    """

    # set the row connection
    ground_column = cp.zeros(len(network.circuit))
    ground_column[wire_idx] = 1 / resistance

    # add row to bottom
    network.circuit = cp.vstack([network.circuit, ground_column])

    # transform to column and add to right
    ground_column = cp.pad(ground_column, (0, 1), 'constant')
    network.circuit = cp.hstack([network.circuit, ground_column.reshape(-1, 1)])

    # increment number of grounds
    network.ground_count += 1


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
    return cp.asarray(matrix)
