import cupy as cp

from nn_simulator import non_ground_selection, minimum_distance_selection
from nn_simulator.model.device.network import Network


def test_non_ground_selection():
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
    viable_nodes = non_ground_selection(network)
    assert len(viable_nodes) == len(circuit) - network.device_grounds
    assert viable_nodes == {0, 1}


def test_minimum_distance_selection_0_distance():
    adj = cp.array([
        [0, 1, 0, 1],
        [1, 0, 1, 0],
        [0, 1, 0, 1],
        [1, 0, 1, 0]
    ], dtype=cp.float32)
    network = Network(adj, tuple(), tuple(), adj, adj, adj, device_grounds=0)
    assert minimum_distance_selection([0], 0)(network, list()) == {1, 2, 3}


def test_minimum_distance_selection_0_distance_ground():
    adj = cp.array([
        [0, 1, 0, 1],
        [1, 0, 1, 0],
        [0, 1, 0, 1],
        [1, 0, 1, 0]
    ], dtype=cp.float32)
    network = Network(adj, tuple(), tuple(), adj, adj, adj, device_grounds=1)
    assert minimum_distance_selection([0], 0)(network, list()) == {1, 2}


def test_minimum_distance_selection_1_distance():
    adj = cp.array([
        [0, 1, 0, 1],
        [1, 0, 1, 0],
        [0, 1, 0, 1],
        [1, 0, 1, 0]
    ], dtype=cp.float32)
    network = Network(adj, tuple(), tuple(), adj, adj, adj, device_grounds=0)
    assert minimum_distance_selection([0], 1)(network, list()) == {2}


def test_minimum_distance_selection_1_distance_ground():
    adj = cp.array([
        [0, 1, 0, 1],
        [1, 0, 1, 0],
        [0, 1, 0, 1],
        [1, 0, 1, 0]
    ], dtype=cp.float32)
    network = Network(adj, tuple(), tuple(), adj, adj, adj, device_grounds=1)
    assert minimum_distance_selection([0], 1)(network, list()) == {2}


def test_minimum_distance_selection_3_distance():
    adj = cp.array([
        [0, 1, 0, 0, 0, 0],
        [1, 0, 1, 0, 0, 0],
        [0, 1, 0, 1, 0, 0],
        [0, 0, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0]
    ], dtype=cp.float32)
    network = Network(adj, tuple(), tuple(), adj, adj, adj, device_grounds=0)
    assert minimum_distance_selection([0], 3)(network, list()) == {4, 5}


def test_minimum_distance_selection_3_distance_ground():
    adj = cp.array([
        [0, 1, 0, 0, 0, 0],
        [1, 0, 1, 0, 0, 0],
        [0, 1, 0, 1, 0, 0],
        [0, 0, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0]
    ], dtype=cp.float32)
    network = Network(adj, tuple(), tuple(), adj, adj, adj, device_grounds=1)
    assert minimum_distance_selection([0], 3)(network, list()) == {4}


def test_minimum_distance_selection_3_distance_negated():
    adj = cp.array([
        [0, 1, 0, 0, 0],
        [1, 0, 1, 0, 0],
        [0, 1, 0, 1, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0]
    ], dtype=cp.float32)
    network = Network(adj, tuple(), tuple(), adj, adj, adj, device_grounds=0)
    function = minimum_distance_selection([0], 3, True)
    assert function(network, list()) == {0, 1, 2, 3}


def test_minimum_distance_selection_3_distance_negated_ground():
    adj = cp.array([
        [0, 1, 0, 0, 0, 1],
        [1, 0, 1, 0, 0, 0],
        [0, 1, 0, 1, 0, 0],
        [0, 0, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0]
    ], dtype=cp.float32)
    network = Network(adj, tuple(), tuple(), adj, adj, adj, device_grounds=1)
    function = minimum_distance_selection([0], 3, True)
    assert function(network, list()) == {0, 1, 2, 3}


test_non_ground_selection()
test_minimum_distance_selection_0_distance()
test_minimum_distance_selection_0_distance_ground()
test_minimum_distance_selection_1_distance()
test_minimum_distance_selection_1_distance_ground()
test_minimum_distance_selection_3_distance()
test_minimum_distance_selection_3_distance_ground()
test_minimum_distance_selection_3_distance_negated()
test_minimum_distance_selection_3_distance_negated_ground()
