import networkx as nx

from nanowire_network_simulator.model.device.network import Network


def nn2nx(network: Network) -> nx.Graph:
    """
    Converts a nanowire network from the matrix format to a Networkx graph.

    Parameters
    ----------
    network: Network
        Matrix format of the nanowire network
    Returns
    -------
    A Networkx graph with all the information (voltage, conductance, etc.) in
    nodes and edges as fields
    """

    graph = nx.from_numpy_matrix(network.adjacency)

    # add wire voltage to nodes
    for n in graph.nodes():
        graph.nodes[n]['V'] = float(network.voltage[n])

    # add junction tension to edge
    for u, v in graph.edges():
        graph[u][v]['V'] = float(network.voltage[u] - network.voltage[v])

    # add junction conductance to edge
    for u, v in graph.edges():
        graph[u][v]['Y'] = float(network.circuit[u, v])

    # add wires position to node
    xs, ys = network.wires_position
    for n in graph.nodes():
        graph.nodes[n]['pos'] = tuple(map(float, (xs[n, n], ys[n, n])))

    # add junction position to edge
    xs, ys = network.junctions_position
    for u, v in graph.edges():
        graph[u][v]['jx_pos'] = tuple(map(float, (xs[u, v], ys[u, v])))

    return graph
