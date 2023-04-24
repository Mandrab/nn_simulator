import numpy as np

from nn_simulator import default as i_default
from nn_simulator.controller.backup import save, exist, read
from nn_simulator.model.device.factory import nanowire_network
from nn_simulator.model.device.networks import generate_network_data
from test.model.device.utils import equals


def test_save_and_import_completeness():
    i_data = generate_network_data(i_default)
    i_nn = nanowire_network(i_data, 0.2, 3)
    i_connections = {'a': 1, 'b': 2}

    save(i_default, i_nn, i_data, i_connections)
    assert all(exist())

    f_nn, f_datasheet, f_data, f_connections = read()

    equals(i_nn, f_nn)

    assert i_default == f_datasheet

    for k, v in i_data.items():
        assert k in f_data
        assert np.allclose(v, f_data[k])

    assert i_connections == f_connections
