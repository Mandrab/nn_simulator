import random

from networkx import Graph


def random_ground(graph: Graph) -> int:
    """Select a random ground node"""

    return random.randint(0, graph.number_of_nodes())


def random_sources(graph: Graph, ground: int, count: int) -> [int]:
    """Select node sources from non-ground nodes"""

    # select nodes that are available to be chosen as sources
    viable_nodes = [*{*graph.nodes()} - {ground}]

    # get a 'count' number of random available nodes
    return [
        viable_nodes.pop(random.randint(0, len(viable_nodes)))
        for _ in range(count)
    ]
