import cupy as cp

from nanowire_network_simulator.model.device.network import Network
from nanowire_network_simulator.model.device.networks import to_cp


def delta_voltage(network: Network) -> cp.ndarray:
    """
    Calculate delta voltage on a junction.

    Parameters
    ----------
    network: NanowireNetwork
        target of the calculation
    Returns
    -------
    An ndarray representing the voltage difference on each junction
    """

    adj, voltage = to_cp(network.adjacency), to_cp(network.voltage)
    return cp.absolute(adj * (voltage.reshape(-1, 1) - adj * voltage))


def calculate_currents(network: Network) -> cp.ndarray:
    """
    Define currents in the network multiplying voltages and conductances.

    Parameters
    ----------
    network: Network
        the nanowire network in which calculate the currents
    Returns
    -------
    A matrix with the current value specified in the node-node intersection
    """

    return to_cp(delta_voltage(network)) * to_cp(network.circuit)
