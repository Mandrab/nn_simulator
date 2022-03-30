import cupy as cp
import numpy as np

from nanowire_network_simulator.model.device.datasheet.Datasheet import default
from nanowire_network_simulator.model.device.network import Network
from nanowire_network_simulator.model.device.network import connect


def test_load_connection():
    """
            [V]|---/\/[R]\/\---[A]---/\/[R]\/\---[B]
                               to
    [V]|---/\/[R]\/\---[A]---/\/[R]\/\---[B]---/\/[R]\/\---[G]
                              ===
     V   0 1 0
     A   1 0 1
     B   0 1 0
        to
    V   0 1 0 0
    A   1 0 1 0
    B   0 1 0 1
    G   0 0 1 0
    """

    initial = 10e-3 * np.array([
        [0, 1, 0],
        [1, 0, 1],
        [0, 1, 0]
    ])

    final = 10e-3 * np.array([
        [0, 1, 0, 0],
        [1, 0, 1, 0],
        [0, 1, 0, 1],
        [0, 0, 1, 0]
    ])

    network = Network(
        adjacency=cp.zeros((1, 1)),
        wires_position=tuple(), junctions_position=tuple(),
        circuit=initial,
        admittance=cp.zeros((1, 1)),
        voltage=cp.zeros((1, 1)),
        ground_count=1
    )
    connect(network, wire_idx=2, resistance=1 / default.Y_min)

    assert cp.allclose(network.circuit, cp.array(final), 10e-3, 10e-3)


test_load_connection()
