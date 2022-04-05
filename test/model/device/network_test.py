import cupy as cp

from nn_simulator.model.device.datasheet.Datasheet import default
from nn_simulator.model.interface.connector import connect
from test.model.device.utils import simple_network


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

    initial = 10e-3 * cp.array([
        [0, 1, 0],
        [1, 0, 1],
        [0, 1, 0]
    ], dtype=cp.float32)

    final = 10e-3 * cp.array([
        [0, 1, 0, 0],
        [1, 0, 1, 0],
        [0, 1, 0, 1],
        [0, 0, 1, 0]
    ], dtype=cp.float32)

    network = simple_network(initial, 1)
    connect(network, wire_idx=2, resistance=1 / default.Y_min)

    assert cp.allclose(network.circuit, final, 10e-3, 10e-3)
