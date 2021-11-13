import random

from networkx import Graph
from typing import Set, Tuple, Callable


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


def random_loads(
        graph: Graph,
        avoid: Set[int],
        count: int = 1,
        resistance_supplier: Callable[[], float] = lambda: random.gauss(1, 2)
) -> Set[Tuple[int, float]]:
    """
    Returns randomly connected loads (e.g. motors).
    The tuple represents the output node and the load resistance.
    """

    return {
        (node, resistance_supplier())
        for node in random_nodes(graph, avoid, count)
    }
