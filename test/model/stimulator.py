import cupy as cp

from nn_simulator import default
from nn_simulator.model.device.network import Network
from nn_simulator.model.stimulator import modified_voltage_node_analysis
from nn_simulator.model.stimulator import update_conductance

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


def evaluate_mna_samples(circuit: cp.ndarray, expected_result: cp.ndarray):
    network = Network(
        adjacency=cp.zeros_like(circuit),
        wires_position=tuple(), junctions_position=tuple(),
        circuit=circuit,
        admittance=cp.zeros_like(circuit),
        voltage=cp.zeros((1, len(circuit))),
        device_grounds=1
    )
    modified_voltage_node_analysis(network, {0: 5.00})
    assert cp.allclose(network.voltage[:-1], expected_result)


def test_samples():
    for circuit, expected_result in samples:
        evaluate_mna_samples(cp.asarray(circuit), cp.asarray(expected_result))


# # delta voltage calculation
# voltage = cp.array([7, 5, 0], dtype=cp.float32)
# adj = cp.array([
#     [0, 1, 0],
#     [1, 0, 0],
#     [0, 0, 0]
# ], dtype=cp.float32)
# print(cp.absolute(adj * (voltage.reshape(-1, 1) - adj * voltage)))


def test_non_stimulated_change():
    circuit = cp.array([
        [0, 1, 0],
        [1, 0, 1],
        [0, 1, 0]
    ], dtype=cp.float32)
    network = Network(
        adjacency=circuit.copy(),
        wires_position=tuple(), junctions_position=tuple(),
        circuit=circuit,
        admittance=cp.zeros_like(circuit),
        voltage=cp.zeros((1, len(circuit))),
        device_grounds=1
    )

    # update the network to let the simulator converge to stable values
    update_conductance(network, default, 1.0)
    initial = network.circuit.copy()

    # update an additional time and get the network state
    update_conductance(network, default, 1.0)
    assert cp.allclose(initial, network.circuit, atol=10e-3)


def test_stimulated_change():
    circuit = cp.array([
        [0, 1, 0, 0],
        [1, 0, 1, 0],
        [0, 1, 0, 1],
        [0, 0, 1, 0]
    ], dtype=cp.float32)
    network = Network(
        adjacency=circuit.copy(),
        wires_position=tuple(), junctions_position=tuple(),
        circuit=circuit,
        admittance=cp.zeros_like(circuit),
        voltage=cp.zeros((1, len(circuit))),
        device_grounds=1
    )

    # update the network to let the simulator converge to stable values
    update_conductance(network, default, 1.0)
    initial = network.circuit.copy()

    # stimulate the network with a non-zero input signal
    modified_voltage_node_analysis(network, {0: 5.00})

    # update an additional time and get the network state
    update_conductance(network, default, 0.1)
    assert not cp.allclose(initial, network.circuit, atol=10e-3)


test_samples()
test_non_stimulated_change()
test_stimulated_change()
