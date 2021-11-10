import random

from networkx import Graph
from typing import Set


def random_nodes(graph: Graph, avoid: Set[int], count: int = 1) -> Set[int]:
    """
    Select random nodes from graph, avoiding the specified ones.
    It can be used, for example, to pick nodes that are not ground.
    """

    viable_nodes = [*{*graph.nodes()} - avoid]

    # get a 'count' random available nodes
    return {
        viable_nodes.pop(random.randrange(len(viable_nodes)))
        for _ in range(count)
    }
