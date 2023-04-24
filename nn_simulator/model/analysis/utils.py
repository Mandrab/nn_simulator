import numpy as np

from nn_simulator.model.device.network import Network


def delta_voltage(network: Network) -> np.ndarray:
    """
    Calculate delta voltage on a junction.

    Parameters
    ----------
    network: NanowireNetwork
        target of the calculation
    Returns
    -------
    An cupy ndarray representing the voltage difference on each junction.
    """

    adj, voltage = network.adjacency, network.voltage
    return np.absolute(adj * (voltage.reshape(-1, 1) - adj * voltage))


def calculate_currents(network: Network) -> np.ndarray:
    """
    Define currents in the network multiplying voltages and conductances.

    Parameters
    ----------
    network: Network
        the nanowire network in which calculate the currents
    Returns
    -------
    A matrix with the current value specified in the node-node intersection.
    """

    return delta_voltage(network) * network.circuit
