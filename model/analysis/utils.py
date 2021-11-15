import numpy as np


def calculate_currents(graph):
    """Define current directions in the network through a directed graph"""

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


def calculate_network_resistance(H, source_node):
    """Calculate the resistance of the network todo atm it doesn't make sense"""

    return H.nodes[source_node]['V'] / calculate_current_flow(H, source_node)


def calculate_source_voltage(graph, node):
    """Extract voltage value from the specific node"""

    return graph.nodes[node]['V']


def calculate_current_flow(graph, node):
    """Calculate current flowing from node as outgoing currents"""

    return sum(filter(
        lambda v: v > 0,    # take only positive currents (outgoing)
        [graph[u][v]['I'] for u, v in graph.edges(node)]
    ))
