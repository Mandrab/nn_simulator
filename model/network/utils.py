import numpy as np


# MODIFIED NODE ANALYSIS FOR VOLTAGES
def modified_voltage_node_analysis(device, v_ins):
    graph = device.connected_nodes[0]
    nodes_count = graph.number_of_nodes()
    sources_count = len(device.source_nodes)

    # sort source-voltage pairs by source id
    # necessary because B, Z, and output vector's values must be in same order ->
    #   -> easiest way is to sort it
    v_ins = sorted(v_ins)

    # create a vector to contain the voltages of the input nodes
    Z = np.zeros(nodes_count)
    for source, voltage in v_ins:
        Z[source] = voltage

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
    for node_idx in range(nodes_count):

        # ignore arcs connected with ground nodes
        if node_idx in device.ground_nodes:
            continue

        for neighbor_idx in graph.neighbors(node_idx):
            # get the edge that connect the two nodes
            edge = graph[node_idx][neighbor_idx]

            # add conductance in matrix - divided by 1.
            # the slot contains the sum of the conductance of the edges
            # connected to the node
            Gs[node_idx][node_idx] += edge['Y']

            # skip if the edge goes to a ground node
            if neighbor_idx in device.ground_nodes:
                continue

            # set the negative conductance to the slot that represent the
            # opposite side node (depends only on the given edge)
            Gs[node_idx][neighbor_idx] = -edge['Y']

    # add sources conductance as the last column of the matrix
    Y = np.hstack((Gs, B))

    # add a slot in the sources array
    B = np.vstack((B, np.zeros(shape=(1, 1))))
    B = np.transpose(B)

    # construct Y matrix as a combination of G, B, D in the form [(G B); (B' D)]
    # add the sources also to the bottom of the matrix
    Y = np.vstack((Y, B))

    # drop ground columns and rows: empty and does not allow matrix inversion
    Y = np.delete(Y, device.ground_nodes, 1)
    Y = np.delete(Y, device.ground_nodes, 0)

    # perform analysis of the circuit (Yx = z -> x = Y^(-1)z)
    # get an iterator in that it will be cycled only once
    results = iter(np.matmul(np.linalg.inv(Y), Z))

    # add calculated voltage as attribute of non-ground nodes
    for idx in graph.nodes() - set(device.ground_nodes):
        graph.nodes[idx]['V'] = next(results)

    # set voltage for ground nodes to 0
    for idx in device.ground_nodes:
        graph.nodes[idx]['V'] = 0

    # DEFINE CURRENT DIRECTION

    # transform graph to a direct graph H
    H = graph.to_directed()

    # add current as a node attribute
    for u, v in H.edges():
        H[u][v]['I'] = (H.nodes[u]['V'] - H.nodes[v]['V']) * H[u][v]['Y']
        H[u][v]['Irounded'] = np.round(H[u][v]['I'], 2)

    # set current direction
    for u in H.nodes():  # select current direction
        for v in H.nodes():
            if H.has_edge(u, v) and H.has_edge(v, u):
                if H[u][v]['I'] < 0:
                    H.remove_edge(u, v)
                else:
                    H.remove_edge(v, u)

    return H
