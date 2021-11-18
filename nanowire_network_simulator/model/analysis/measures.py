import logging
import networkx as nx

from nanowire_network_simulator.model.device.utils import largest_component
from networkx import Graph
from typing import Dict, Callable

__FORMAT = f'The %s is: %s'

global_statistics: Dict[str, Callable[[Graph], str]] = {
    'number of nodes':
        lambda graph: graph.number_of_nodes(),
    'number of edges (junctions)':
        lambda graph: graph.number_of_edges(),
    'degree of node':
        lambda graph: [val for (node, val) in graph.degree()],
    'clustering of node':
        lambda graph: [n for n in nx.clustering(graph)],
    'number of connected components':
        lambda graph: nx.number_connected_components(graph),
    'number of isolated nodes':
        lambda graph: len([x for x in nx.isolates(graph)]),
    'number of nodes in the largest component':
        lambda graph: len(max(nx.connected_components(graph), key=len))
}

largest_component_statistics: Dict[str, Callable[[Graph], str]] = {
    'diameter of the largest connected component':
        lambda graph: nx.diameter(graph),
    'average shortest path length of the largest connected component':
        lambda graph: nx.average_shortest_path_length(graph, weight=None),
    'average clustering coefficient of the largest connected component':
        lambda graph: nx.average_clustering(graph),
    'sigma small-world coefficient of the largest connected component':
        lambda graph: nx.sigma(graph, niter=100, nrand=10, seed=None),
    'omega small-world coefficient of the largest connected component':
        lambda graph: nx.omega(graph, niter=100, nrand=10, seed=None)
}


def print_info(key: str, graph: Graph):
    """Print a specific measure of the network"""

    if key in global_statistics:
        logging.info(__FORMAT % (key, str(global_statistics[key](graph))))

    if key in largest_component_statistics:
        logging.info(__FORMAT % (key, largest_component_statistics[key](graph)))


def inspect(graph: Graph):
    """Print all the measures/statistics of the graph"""

    for key in global_statistics:
        logging.info(__FORMAT % (key, global_statistics[key](graph)))

    # ANALYSIS OF THE LARGEST CONNECTED COMPONENT
    graph = largest_component(graph)

    for key in largest_component_statistics:
        logging.info(__FORMAT % (key, largest_component_statistics[key](graph)))
