import numpy as np

from functools import cache


# MODIFIED VOlTAGE NODE ANALYSIS
def modified_voltage_node_analysis(device, v_ins):
    graph = device.connected_nodes[0]
    nodes_count = graph.number_of_nodes()
    sources_count = len(device.source_nodes)
    grounds_count = len(device.ground_nodes)

    # create a matrix to store voltages of nodes
    # for now, it only contains sources voltages # todo maybe sort sources from key
    voltages = np.vstack((
        np.zeros(shape=(nodes_count - sources_count, 1)),   # zeroed voltages
        np.array([[*map(lambda pair: pair[1], v_ins)]]).T   # voltage inputs
    )) # matZ

    # create a matrix that stores the sum of the conductances of the edges
    # of a node
    conductances = np.zeros(shape=(
        nodes_count - grounds_count,
        nodes_count - grounds_count
    )) # matG

    # create a matrix to identify the sources
    sources = np.zeros(shape=(nodes_count - grounds_count, 1)) # matB

    # filling Y matrix as a combination of G B D in the form [(G B) ; (B' D)]

    # row and col idx in conductance matrix
    row_idx = 0

    # define a function for the correct indexing in the matrix
    @cache
    def smaller_grounds(index):
        return len([g for g in device.ground_nodes if g < index])

    # find conductance of edges
    for node_idx in range(nodes_count):

        # ignore arcs connected with ground nodes todo why?
        if node_idx in device.ground_nodes:
            continue

        for neighbor_idx in graph.neighbors(node_idx):
            # get the edge that connect the two nodes
            edge = graph[node_idx][neighbor_idx]

            # add conductance in matrix - divided by 1.
            # the slot contains the sum of the conductance of the edges
            # connected to the node
            conductances[row_idx][row_idx] += edge['Y']

            # skip if the edge goes to a ground node
            if neighbor_idx in device.ground_nodes:
                continue

            # check column idx where to add the conductance: since ground
            # nodes column are not present, adjust the index
            col_idx = neighbor_idx - smaller_grounds(neighbor_idx)

            # set the negative conductance to the slot that represent the
            # opposite side node (depends only on the given edge)
            conductances[row_idx][col_idx] = -edge['Y']

        # fill the next row with the data of another node
        row_idx += 1

    # set conductance of sources equal to 1
    for source in device.source_nodes:
        ground_count = smaller_grounds(source)
        sources[source - ground_count] = 1

    # add sources conductance as the last column of the matrix
    conductances = np.hstack((conductances, sources))

    # add a slot in the sources array
    sources = np.hstack((
        np.transpose(sources),  # make an array from a column
        np.zeros(shape=(1, 1))  # single slot to add
     ))

    # add the sources also to the bottom of the matrix
    conductances = np.vstack((conductances, sources)) # matY

    # solve X matrix from Yx = z
    voltages = np.matmul(
        np.linalg.inv(conductances),
        voltages
    )  # Ohm law; matX # todo maybe dot: is parallel but change something

    # add voltage as a node attribute
    for n in graph.nodes():
        if n in device.ground_nodes:
            graph.nodes[n]['V'] = 0
        else:
            graph.nodes[n]['V'] = voltages[n - smaller_grounds(n)][0]

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
