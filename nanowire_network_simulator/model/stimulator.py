import cupy as cp

from typing import Dict
from .device import Datasheet
from nanowire_network_simulator.model.device.network import Network


def stimulate(
        graph: Network,
        datasheet: Datasheet,
        delta_time: float,
        inputs: Dict[int, float]
):
    """
    Stimulate the network through voltage-inputs on given pins.
    The function directly modify the passed graph.

    Parameters:
    ----------
    graph: Graph
        The network to stimulate
    datasheet: Datasheet
        The datasheet of the characteristics of the device
    delta_time: float
        The time elapsed from the last update
    inputs: Dict[int, float],
        Pair of source/nodes with, for each, the correspondent voltage value
    """

    # update weights of the edges. they need to be initialized
    update_conductance(graph, datasheet, delta_time)

    # update voltage values of the nodes of the system after the stimulation
    modified_voltage_node_analysis(graph, inputs)


def update_conductance(graph: Network, datasheet: Datasheet, delta_time: float):
    """Update edges weights (Miranda's model)"""

    # calculate delta voltage on a junction
    delta_v = graph.device.adjacency * graph.device.voltage
    delta_v = cp.absolute(graph.device.voltage.reshape(-1, 1) - delta_v)

    # excitation and depression rate coefficients
    kp = datasheet.kp0 * cp.exp(datasheet.eta_p * delta_v)
    kd = datasheet.kd0 * cp.exp(-datasheet.eta_d * delta_v)
    kpd = kp + kd

    # calculate and set admittance [0-1]
    partial = kd / kp * graph.device.admittance * cp.exp(-delta_time * kpd)
    graph.device.admittance = graph.device.adjacency * kp / kpd * (1 + partial)

    # calculate and set circuit conductance
    partial = graph.device.admittance * (datasheet.Y_max - datasheet.Y_min)
    graph.device.circuit = graph.device.adjacency * (datasheet.Y_min + partial)


def modified_voltage_node_analysis(network: Network, inputs: Dict[int, float]):
    """
    Execute the Modified Nodal Analysis for voltages calculation.

    Parameters
    ----------
    network: the nanowire network circuit
    inputs: a pair of node input index and applied voltage
    """

    # create a vector to contain the voltages of the input nodes
    # the ground nodes are not present
    voltages = [v for _, v in sorted(inputs.items())]
    voltages = cp.asarray(voltages, dtype=cp.float32)
    Z = cp.append(cp.zeros(network.wires), voltages)

    # create a vector to identify the sources (1: source, 0: non-source)
    # each column contains only one '1': there is 1 column for each source
    B = cp.zeros((network.wires, len(inputs)))
    for idx, source in enumerate(inputs):
        B[source][idx] = 1

    # stores the sum of the conductances of the edges incident on a node
    # each row refer to a specific node and the index r,c represent the
    # conductance in the arch from node r to c
    G = cp.negative(network.circuit)
    summa = cp.negative(cp.sum(G, axis=1))
    cp.fill_diagonal(G, summa)

    # add sources identifiers as the last column of the matrix
    Y = cp.hstack((G[:-network.grounds, :-network.grounds], B))

    # add a slot in the sources array
    B = cp.vstack((B, cp.zeros((len(inputs), len(inputs)))))
    B = cp.transpose(B)

    # construct Y matrix as a combination of G, B, D in the form [(G B); (B' D)]
    # add the sources also to the bottom of the matrix
    Y = cp.vstack((Y, B))

    # perform analysis of the circuit (Yx = z -> x = Y^(-1)z)
    network.voltage = cp.matmul(cp.linalg.inv(Y), Z)[:-len(inputs)]
    network.voltage = cp.pad(network.voltage, (0, network.grounds))
