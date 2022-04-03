import cupy as cp

from nanowire_network_simulator import default as i_default
from nanowire_network_simulator.controller.backup import save, exist, read
from nanowire_network_simulator.model.device.factory import nanowire_network
from nanowire_network_simulator.model.device.networks import \
    generate_network_data


def test_save_and_import_completeness():
    i_data = generate_network_data(i_default)
    i_nn = nanowire_network(i_data, 0.2, 3)
    i_connections = {'a': 1, 'b': 2}

    save(i_default, i_nn, i_data, i_connections)
    assert all(exist())

    f_nn, f_datasheet, f_data, f_connections = read()

    assert cp.allclose(i_nn.adjacency, f_nn.adjacency)
    assert cp.allclose(i_nn.wires_position[0], f_nn.wires_position[0])
    assert cp.allclose(i_nn.wires_position[1], f_nn.wires_position[1])
    assert cp.allclose(i_nn.junctions_position[0], f_nn.junctions_position[0])
    assert cp.allclose(i_nn.junctions_position[1], f_nn.junctions_position[1])
    assert cp.allclose(i_nn.circuit, f_nn.circuit)
    assert cp.allclose(i_nn.admittance, f_nn.admittance)
    assert cp.allclose(i_nn.voltage, f_nn.voltage)
    assert i_nn.grounds == f_nn.grounds

    assert i_default == f_datasheet

    for k, v in i_data.items():
        assert k in f_data
        assert cp.allclose(v, f_data[k])

    assert i_connections == f_connections


test_save_and_import_completeness()
