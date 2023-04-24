import numpy as np

from nn_simulator.model.device.network import Network


def stack(matrix: np.ndarray, array: np.ndarray) -> np.ndarray:
    # add row to bottom
    matrix = np.vstack([matrix, array])

    # transform to column and add to right
    array = np.pad(array, (0, 1), 'constant').reshape(-1, 1)
    return np.hstack([matrix, array])


def equals(n1: Network, n2: Network):
    assert np.allclose(n1.adjacency, n2.adjacency)
    assert np.allclose(n1.wires_position[0], n2.wires_position[0])
    assert np.allclose(n1.wires_position[1], n2.wires_position[1])
    assert np.allclose(n1.junctions_position[0], n2.junctions_position[0])
    assert np.allclose(n1.junctions_position[1], n2.junctions_position[1])

    assert np.allclose(n1.circuit, n2.circuit, atol=1e-4)
    assert np.allclose(n1.admittance, n2.admittance, atol=1e-3)
    assert np.allclose(n1.voltage, n2.voltage, rtol=1e-3, atol=1e-3)

    assert n1.grounds == n2.grounds


def simple_network(matrix: np.ndarray, grounds=0) -> Network: return Network(
        adjacency=matrix.copy(),
        wires_position=tuple(), junctions_position=tuple(),
        circuit=matrix,
        admittance=np.zeros_like(matrix),
        voltage=np.zeros((1, len(matrix))),
        device_grounds=grounds
    )
