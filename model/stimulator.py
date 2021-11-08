import math

import numpy as np

from networkx import Graph

from model.device.datasheet.Datasheet import Datasheet


def stimulate(
        graph: Graph,
        datasheet: Datasheet,
        delta_time: float,
        inputs: (int, float),
        ground: int
):
    """Stimulate the network through a voltage in a given pin"""

    # update weights of the edges. they need to be initialized
    update_edge_weights(graph, datasheet, delta_time)

    # update voltage values of the nodes of the system after the stimulation
    modified_voltage_node_analysis(graph, inputs, ground)


def update_edge_weights(graph, datasheet, delta_time):
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


def modified_voltage_node_analysis(graph: Graph, inputs: (int, float), ground):
    """Execute modified node analysis for voltages"""

    nodes_count = graph.number_of_nodes()
    sources_count = len(inputs)

    # sort source-voltage pairs by source id
    # necessary because B, Z, and output vector's values must be in same order
    #   -> easiest way is to sort it
    v_ins = sorted(inputs)

    # create a vector to contain the voltages of the input nodes
    Z = np.zeros(nodes_count + sources_count - 1)
    for i, (_, voltage) in enumerate(v_ins):
        Z[nodes_count - 1 + i] = voltage

    # create a vector to identify the sources (1: source, 0: non-source)
    # each column contains only one '1': there is 1 column for each source
    B = np.zeros(shape=(nodes_count, sources_count))
    for idx in range(sources_count):
        source, _ = v_ins[idx]
        B[source][idx] = 1

    # create a matrix that stores the sum of the conductances of the edges
    # incident on a node
    # each row refer to a specific node and the index r,c represent the
    # conductance in the arch from node r to c
    Gs = np.zeros(shape=(nodes_count, nodes_count))

    # find conductance of edges
    for node_idx in graph.nodes:

        # ignore arcs connected with ground nodes
        if node_idx == ground:
            continue

        for neighbor_idx in graph.neighbors(node_idx):
            # get the edge that connect the two nodes
            edge = graph[node_idx][neighbor_idx]

            # add conductance in matrix - divided by 1.
            # the slot contains the sum of the conductance of the edges
            # connected to the node
            Gs[node_idx][node_idx] += edge['Y']

            # skip if the edge goes to a ground node
            if neighbor_idx == ground:
                continue

            # set the negative conductance to the slot that represent the
            # opposite side node (depends only on the given edge)
            Gs[node_idx][neighbor_idx] = -edge['Y']

    # add sources conductance as the last column of the matrix
    Y = np.hstack((Gs, B))

    # add a slot in the sources array
    B = np.vstack((B, np.zeros(shape=(sources_count, sources_count))))
    B = np.transpose(B)

    # construct Y matrix as a combination of G, B, D in the form [(G B); (B' D)]
    # add the sources also to the bottom of the matrix
    Y = np.vstack((Y, B))

    # drop ground columns and rows: empty and does not allow matrix inversion
    Y = np.delete(Y, ground, 1)
    Y = np.delete(Y, ground, 0)

    # perform analysis of the circuit (Yx = z -> x = Y^(-1)z)
    # get an iterator in that it will be cycled only once
    results = iter(np.matmul(np.linalg.inv(Y), Z))

    # add calculated voltage as attribute of non-ground nodes
    for idx in graph.nodes() - {ground}:
        graph.nodes[idx]['V'] = next(results)

    # set voltage for ground nodes to 0
    graph.nodes[ground]['V'] = 0


def voltage_initialization(
        graph: Graph,
        sources: [int],
        ground: int
) -> [(int, float)]:
    """Call modified voltage analysis for an initial setup of the network"""

    stimulus = [(source, 0.01) for source in sources]
    modified_voltage_node_analysis(graph, stimulus, ground)

    return stimulus
