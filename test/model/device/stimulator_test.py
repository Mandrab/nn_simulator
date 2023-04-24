import numpy as np

from nn_simulator import default
from nn_simulator.model.device.network import Network
from nn_simulator.model.stimulator import modified_voltage_node_analysis
from nn_simulator.model.stimulator import update_conductance
from test.model.device.utils import simple_network

samples = [
    (
        # [V]|---/\/[R]\/\---[A]---/\/[R]\/\---|[G]
        [
            [0, 1, 0],
            [1, 0, 1],
            [0, 1, 0]
        ],
        # expected voltage distribution
        [5.00, 2.50]
    ),
    (
        #      |--/\/[R]\/\---[A]---/\/[R]\/\--|
        # [V]--|                               |--[G]
        #      |--/\/[R]\/\---[B]---/\/[R]\/\--|
        [
            [0, 1, 1, 0],
            [1, 0, 0, 1],
            [1, 0, 0, 1],
            [0, 1, 1, 0]
        ],
        # expected voltage distribution
        [5.00, 2.50, 2.50]
    ),
    (
        #                      |--/\/[2R]\/\--[B]--/\/[R]\/\--|
        # [V]---/\/[1.5R]\/\--[A]                             |--[G]
        #                      |--/\/[R]\/\--[C]--/\/[2R]\/\--|
        [
            [0,          1 / 1.5,    0,        0,        0],
            [1 / 1.5,    0,          1 / 2,    1,        0],
            [0,          1 / 2,      0,        0,        1],
            [0,          1,          0,        0,        1 / 2],
            [0,          0,          1,        1 / 2,    0]
        ],
        # expected voltage distribution
        [5.00, 2.50, 0.83333, 1.66666]
    )
]


def evaluate_mna_samples(circuit: np.ndarray, expected_result: np.ndarray):
    network = Network(
        adjacency=circuit > 0,
        wires_position=tuple(), junctions_position=tuple(),
        circuit=circuit,
        admittance=np.zeros_like(circuit),
        voltage=np.zeros((1, len(circuit))),
        device_grounds=1
    )
    modified_voltage_node_analysis(network, {0: 5.00})
    assert np.allclose(network.voltage[:-1], expected_result)


def test_samples():
    for circuit, expected_result in samples:
        evaluate_mna_samples(np.asarray(circuit), np.asarray(expected_result))


def test_non_stimulated_change():
    circuit = np.array([
        [0, 1, 0],
        [1, 0, 1],
        [0, 1, 0]
    ], dtype=np.float32)
    network = simple_network(circuit, 1)

    # update the network to let the simulator converge to stable values
    update_conductance(network, default, 1.0)
    initial = network.circuit.copy()

    # update an additional time and get the network state
    update_conductance(network, default, 1.0)
    assert np.allclose(initial, network.circuit, atol=10e-3)


def test_stimulated_change():
    circuit = np.array([
        [0, 1, 0, 0],
        [1, 0, 1, 0],
        [0, 1, 0, 1],
        [0, 0, 1, 0]
    ], dtype=np.float32)
    network = simple_network(circuit, 1)

    # update the network to let the simulator converge to stable values
    update_conductance(network, default, 1.0)
    initial = network.circuit.copy()

    # stimulate the network with a non-zero input signal
    modified_voltage_node_analysis(network, {0: 5.00})

    # update an additional time and get the network state
    update_conductance(network, default, 0.1)
    assert not np.allclose(initial, network.circuit, atol=10e-3)
