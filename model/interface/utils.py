import random

from networkx import Graph


def random_ground(graph: Graph) -> int:
    """Select a random ground node"""

    return random.randint(0, graph.number_of_nodes())


def random_sources(graph: Graph, ground: int, count: int) -> [int]:
    """Select node sources from non-ground nodes"""

    nodes = [*{*graph.nodes()} - {ground}]
    return [
        nodes.pop(random.randint(0, len(nodes)))
        for _ in range(count)
    ]
