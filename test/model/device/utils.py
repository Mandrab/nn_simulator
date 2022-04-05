import cupy as cp

from nn_simulator.model.device.network import Network


def stack(matrix: cp.ndarray, array: cp.ndarray) -> cp.ndarray:
    # add row to bottom
    matrix = cp.vstack([matrix, array])

    # transform to column and add to right
    array = cp.pad(array, (0, 1), 'constant').reshape(-1, 1)
    return cp.hstack([matrix, array])


def equals(n1: Network, n2: Network):
    assert cp.allclose(n1.adjacency, n2.adjacency)
    assert cp.allclose(n1.wires_position[0], n2.wires_position[0])
    assert cp.allclose(n1.wires_position[1], n2.wires_position[1])
    assert cp.allclose(n1.junctions_position[0], n2.junctions_position[0])
    assert cp.allclose(n1.junctions_position[1], n2.junctions_position[1])

    assert cp.allclose(n1.circuit, n2.circuit, atol=1e-4)
    assert cp.allclose(n1.admittance, n2.admittance, atol=1e-3)
    assert cp.allclose(n1.voltage, n2.voltage, rtol=1e-3, atol=1e-3)

    assert n1.grounds == n2.grounds


def simple_network(matrix: cp.ndarray, grounds=0) -> Network: return Network(
        adjacency=matrix.copy(),
        wires_position=tuple(), junctions_position=tuple(),
        circuit=matrix,
        admittance=cp.zeros_like(matrix),
        voltage=cp.zeros((1, len(matrix))),
        device_grounds=grounds
    )
