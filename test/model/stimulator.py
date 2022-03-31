import cupy as cp

from nanowire_network_simulator.model.device.network import Network
from nanowire_network_simulator.model.stimulator import \
    modified_voltage_node_analysis


samples = [
    (
        # [V]|---/\/[R]\/\---[A]---/\/[R]\/\---|[G]
        #
        # Expected voltage distribution:
        # - V: 5.0
        # - A: 2.5
        # - G: 0.0
        cp.array([
            [0, 1, 0],
            [1, 0, 1],
            [0, 1, 0]
        ]),
        [5.00, 2.50]
    ),
    (
        #      |--/\/[R]\/\---[A]---/\/[R]\/\--|
        # [V]--|                               |--[G]
        #      |--/\/[R]\/\---[B]---/\/[R]\/\--|
        #
        # Expected voltage distribution:
        # - V: 5.0
        # - A: 2.5
        # - B: 2.5
        # - G: 0.0
        cp.array([
            [0, 1, 1, 0],
            [1, 0, 0, 1],
            [1, 0, 0, 1],
            [0, 1, 1, 0]
        ]),
        [5.00, 2.50, 2.50]
    ),
    (
        #                      |--/\/[2R]\/\--[B]--/\/[R]\/\--|
        # [V]---/\/[1.5R]\/\--[A]                             |--[G]
        #                      |--/\/[R]\/\--[C]--/\/[2R]\/\--|
        #
        # Expected voltage distribution:
        # - V: 10.0
        # - A: 5.0
        # - B: 1.67
        # - C: 3.33
        # - G: 0.0
        cp.array([
            [0,          1 / 1.5,    0,        0,        0],
            [1 / 1.5,    0,          1 / 2,    1,        0],
            [0,          1 / 2,      0,        0,        1],
            [0,          1,          0,        0,        1 / 2],
            [0,          0,          1,        1 / 2,    0]
        ]),
        [5.00, 2.50, 0.83333, 1.66666]
    )
]


def evaluate_mna_samples(circuit: cp.ndarray, expected_result: cp.ndarray):
    network = Network(
        adjacency=cp.zeros((1, 1)),
        wires_position=tuple(), junctions_position=tuple(),
        circuit=circuit,
        admittance=cp.zeros((1, 1)),
        voltage=cp.zeros((1, 1)),
        ground_count=1
    )
    modified_voltage_node_analysis(network, {0: 5.00})
    assert cp.allclose(network.voltage[:-1], expected_result)


def test_samples():
    for circuit, expected_result in samples:
        evaluate_mna_samples(circuit, cp.asarray(expected_result))


test_samples()
