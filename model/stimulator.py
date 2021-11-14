import math
import numpy as np

from networkx import Graph
from typing import List, Tuple, Set
from model.device.datasheet.Datasheet import Datasheet
from model.interface.connector import connect

__SHORT_CIRCUIT_RES = 0.0001


def stimulate(
        graph: Graph,
        datasheet: Datasheet,
        delta_time: float,
        inputs: List[Tuple[int, float]],
        outputs: List[Tuple[int, float]],
        grounds: Set[int]
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
    inputs: List[Tuple[int, float]],
        List of source-nodes with, for each, the correspondent voltage value
    outputs: List[Tuple[int, float]]
        List of outputs of the network with the correspondent resistance/load.
        The resistance is considered as the resistance of the arch that bring
        to the ground.
    """

    # update weights of the edges. they need to be initialized
    update_edge_weights(graph, datasheet, delta_time)

    # add weighted edges to simulate output loads. An edge of those is a newly
    # added ground node that is returned by the function to be deleted after
    # the analysis.
    # the vector contains the new grounds used for analysis
    new_grounds = {
        connect(graph, output, resistance)
        for output, resistance in outputs
    }

    # update voltage values of the nodes of the system after the stimulation
    modified_voltage_node_analysis(graph, inputs, grounds | new_grounds)

    # remove the grounds and the edges used for the analysis
    for ground in new_grounds:
        graph.remove_node(ground)


def update_edge_weights(graph: Graph, datasheet: Datasheet, delta_time: float):
    """Update edges weights (Miranda's model)"""

    for u, v in graph.edges():
        edge = graph[u][v]

        edge['deltaV'] = abs(graph.nodes[u]['V'] - graph.nodes[v]['V'])
        edge['kp'] = datasheet.kp0 * math.exp(datasheet.eta_p * edge['deltaV'])
        edge['kd'] = datasheet.kd0 * math.exp(-datasheet.eta_d * edge['deltaV'])
        edge['g'] = (
                edge['kp'] / (edge['kp'] + edge['kd'])
            ) * (
                1 - (
                    1 - (1 + (edge['kd'] / edge['kp']) * edge['g'])
                ) * math.exp(
                    -(edge['kp'] + edge['kd']) * delta_time
                )
            )
        edge['Y'] = datasheet.Y_min*(1 - edge['g']) + datasheet.Y_max*edge['g']
        edge['R'] = 1 / edge['Y']


def modified_voltage_node_analysis(
        graph: Graph,
        inputs: List[Tuple[int, float]],
        grounds: Set[int]
):
    """Execute modified node analysis for voltages"""

    nodes_count = graph.number_of_nodes()
    inputs_count = len(inputs)
    grounds_count = len(grounds)

    # sort source-voltage pairs by source id
    # necessary because B, Z, and output vector's values must be in same order
    #   -> easiest way is to sort it
    v_ins = sorted(inputs)

    # create a vector to contain the voltages of the input nodes
    # the ground nodes are not present
    Z = np.zeros(nodes_count - grounds_count + inputs_count)
    for i, (_, voltage) in enumerate(v_ins):
        Z[nodes_count - grounds_count + i] = voltage

    # create a vector to identify the sources (1: source, 0: non-source)
    # each column contains only one '1': there is 1 column for each source
    B = np.zeros(shape=(nodes_count, inputs_count))
    for idx, (source, _) in enumerate(v_ins):
        B[source][idx] = 1

    # create a matrix that stores the sum of the conductances of the edges
    # incident on a node
    # each row refer to a specific node and the index r,c represent the
    # conductance in the arch from node r to c
    Gs = np.zeros(shape=(nodes_count, nodes_count))

    # find conductance of edges
    for node_idx in graph.nodes:

        # ignore arcs connected with ground nodes
        if node_idx in grounds:
            continue

        for neighbor_idx in graph.neighbors(node_idx):
            # get the edge that connect the two nodes
            edge = graph[node_idx][neighbor_idx]

            # add conductance in matrix - divided by 1.
            # the slot contains the sum of the conductance of the edges
            # connected to the node
            Gs[node_idx][node_idx] += edge['Y']

            # skip if the edge goes to a ground node
            if neighbor_idx in grounds:
                continue

            # set the negative conductance to the slot that represent the
            # opposite side node (depends only on the given edge)
            Gs[node_idx][neighbor_idx] = -edge['Y']

    # add sources identifiers as the last column of the matrix
    Y = np.hstack((Gs, B))

    # add a slot in the sources array
    B = np.vstack((B, np.zeros(shape=(inputs_count, inputs_count))))
    B = np.transpose(B)

    # construct Y matrix as a combination of G, B, D in the form [(G B); (B' D)]
    # add the sources also to the bottom of the matrix
    Y = np.vstack((Y, B))

    # drop ground columns and rows: empty and does not allow matrix inversion
    Y = np.delete(Y, [*grounds], 1)
    Y = np.delete(Y, [*grounds], 0)

    # perform analysis of the circuit (Yx = z -> x = Y^(-1)z)
    # get an iterator in that it will be cycled only once
    results = iter(np.matmul(np.linalg.inv(Y), Z))

    # add calculated voltage as attribute of non-ground nodes
    for idx in graph.nodes() - grounds:
        graph.nodes[idx]['V'] = next(results)

    # set voltage for ground nodes to 0
    for ground in grounds:
        graph.nodes[ground]['V'] = 0


def voltage_initialization(
        graph: Graph,
        sources: Set[int],
        grounds: Set[int]
) -> List[Tuple[int, float]]:
    """Call modified voltage analysis for an initial setup of the network"""

    stimulus = [(source, 0.01) for source in sources]
    modified_voltage_node_analysis(graph, stimulus, grounds)

    return stimulus
