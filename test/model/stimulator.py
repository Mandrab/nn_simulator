import cupy as cp

from nanowire_network_simulator.model.device.network import Network
from nanowire_network_simulator.model.stimulator import \
    modified_voltage_node_analysis


def test_basic_mna():
    """
    [V]|---/\/[R]\/\--[A]--/\/[R]\/\---|[G]
                ===
    V   0 1 0
    A   1 0 1
    G   0 1 0

    Expected voltage distribution:
    - V: 5.0
    - A: 2.5
    - G: 0.0
    """

    circuit = cp.array([
        [0, 1, 0],
        [1, 0, 1],
        [0, 1, 0]
    ])

    network = Network(
        adjacency=cp.zeros((1, 1)),
        wires_position=tuple(), junctions_position=tuple(),
        circuit=circuit,
        admittance=cp.zeros((1, 1)),
        voltage=cp.zeros((1, 1)),
        ground_count=1
    )
    modified_voltage_node_analysis(network, {0: 5})
    assert cp.allclose(network.voltage, cp.array([5, 2.5]), 10e-3, 10e-3)


test_basic_mna()
