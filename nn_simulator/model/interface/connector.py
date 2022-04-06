import cupy as cp

from nn_simulator.model.device.network import Network
from nn_simulator.model.utils import stack


def connect(network: Network, wire_idx: int, resistance: float):
    """
    Connect an external load to the network.

    Parameters
    ----------
    network: Network
        the nanowire network to connect the load to
    wire_idx: int
        index of the connection node of the nanowire network
    resistance: float
        resistance of the attached load
    """

    # set the row connection
    ground_pad = cp.zeros(len(network.adjacency))
    ground_pad[wire_idx] = 1 / resistance

    # pad the matrix with the column on right and bottom
    network.adjacency = stack(network.adjacency, ground_pad)
    network.circuit = stack(network.circuit, ground_pad)
    network.admittance = stack(network.admittance, ground_pad)
    network.voltage = cp.pad(network.voltage, (0, 1))

    # increment number of grounds
    network.external_grounds += 1


def disconnect(network: Network):
    """
    Disconnect all the external loads of the network.

    Parameters
    ----------
    network: Network
        the nanowire network from which disconnect the loads
    """

    # if there are not external grounds, return
    if not (grounds := network.external_grounds):
        return

    # remove paddings from the matrix
    network.adjacency = network.adjacency[:-grounds, :-grounds]
    network.circuit = network.circuit[:-grounds, :-grounds]
    network.admittance = network.admittance[:-grounds, :-grounds]
    network.voltage = network.voltage[:-grounds]

    # decrement number of grounds
    network.external_grounds = 0
