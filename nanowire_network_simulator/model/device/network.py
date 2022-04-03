import cupy as cp
import numpy as np

from dataclasses import dataclass
from scipy.sparse.csgraph import connected_components
from test.model.utils import stack
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
    grounds: int
        specify the number of nodes to be considered ground (those have to be at
        the rightmost part of the matrix)
    """

    adjacency: cp.ndarray
    wires_position: Tuple[cp.ndarray, cp.ndarray]
    junctions_position: Tuple[cp.ndarray, cp.ndarray]

    circuit: cp.ndarray
    admittance: cp.ndarray
    voltage: cp.ndarray

    grounds: int = 0

    @property
    def nodes(self) -> int:
        """
        Returns the number of nodes composing the circuit, including grounds.

        Returns
        -------
        An integer representing the number of different nodes of the circuit:
            # wires + # grounds
        """
        return len(self.adjacency)

    @property
    def wires(self) -> int:
        """
        Returns the number of wires composing the circuit, excluding grounds.

        Returns
        -------
        An integer representing the number of different wires of the circuit.
        """
        return len(self.adjacency) - self.grounds


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
        grounds=grounds
    )


def copy(network: Network, ram: bool = True) -> Network:
    """
    Makes a deep copy of the nanowire network.

    Parameters
    ----------
    network: Network
        the network to copy
    ram: bool
        specify if the copied system should remain in the gpu memory or be moved
        to the RAM
    Returns
    -------
    A copy of the input nanowire network
    """
    xw, yw = network.wires_position
    xj, yj = network.junctions_position

    adj = cp.asnumpy(network.adjacency) if ram else network.adjacency.copy()
    wp = (
        cp.asnumpy(xw) if ram else xw.copy(),
        cp.asnumpy(yw) if ram else yw.copy()
    )
    jp = (
        cp.asnumpy(xj) if ram else xj.copy(),
        cp.asnumpy(yj) if ram else yj.copy()
    )
    circuit = cp.asnumpy(network.circuit) if ram else network.circuit.copy()
    adm = cp.asnumpy(network.admittance) if ram else network.admittance.copy()
    voltage = cp.asnumpy(network.voltage) if ram else network.voltage.copy()

    return Network(adj, wp, jp, circuit, adm, voltage, network.grounds)


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
    ground_pad = cp.zeros(len(network.adjacency))
    ground_pad[wire_idx] = 1 / resistance

    # pad the matrix with the column on right and bottom
    network.adjacency = stack(network.adjacency, ground_pad)
    network.circuit = stack(network.circuit, ground_pad)
    network.admittance = stack(network.admittance, ground_pad)
    network.voltage = cp.pad(network.voltage, (0, 1))

    # increment number of grounds
    network.grounds += 1


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
