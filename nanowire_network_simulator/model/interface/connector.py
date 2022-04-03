import cupy as cp

from nanowire_network_simulator.model.device.network import Network
from test.model.utils import stack


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
