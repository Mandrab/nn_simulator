import numpy as np

from networkx import Graph
from typing import List


def calculate_currents(graph: Graph) -> Graph:
    """Define current directions in the network through a directed graph"""

    # transform graph to a direct graph graph
    graph = graph.to_directed()

    # calculate and add current as a edge attribute
    for u, v in graph.edges():
        delta_v = graph.nodes[u]['V'] - graph.nodes[v]['V']
        edge_admittance = graph[u][v]['Y']

        graph[u][v]['I'] = delta_v * edge_admittance
        graph[u][v]['I_rounded'] = np.round(graph[u][v]['I'], 2)

    # remove negative arches (there already is a positive, opposite arch)
    for u in graph.nodes():
        for v in graph.nodes():

            # if at least one of the arches has been deleted, continue
            if not graph.has_edge(u, v) or not graph.has_edge(v, u):
                continue

            # one of the arches has to be removed
            if graph[u][v]['I'] < 0:
                graph.remove_edge(u, v)
            else:
                graph.remove_edge(v, u)

    return graph


def node_voltage(graph: Graph, node: int) -> float:
    """Extract voltage value from the specific node"""

    return graph.nodes[node]['V']


def current_flow(graph: Graph, node: int) -> float:
    """Calculate current flowing out / exiting a node"""

    return sum(filter(
        lambda _: _ > 0,    # take only positive currents (outgoing)
        [graph[u][v]['I'] for u, v in graph.edges(node)]
    ))


def calculate_network_currents(graph: Graph, sources: List[int]) -> float:
    """Calculate the currents entering the network (from sources)"""

    return sum([current_flow(graph, node) for node in sources])
