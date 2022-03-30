import cupy as cp

from nanowire_network_simulator.model.device.network import Network


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

    partial = network.adjacency * network.voltage
    partial = network.voltage.reshape(-1, 1) - partial
    return cp.absolute(network.adjacency * partial)


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

    return delta_voltage(network) * network.circuit
