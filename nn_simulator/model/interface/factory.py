import random

from nn_simulator.model.device.network import Network
from typing import Set, Callable, Dict

__NO_VIABLE_NODE_ERROR = "Not enough nodes respect the required properties"


def random_nodes(network: Network, avoid: Set[int], count: int = 1) -> Set[int]:
    """
    Select random nodes from graph, avoiding the specified ones. It can be used,
    for example, to pick nodes that are not ground. If no viable nodes are
    present, throw an error.

    Parameters
    ----------
    network: Network
        The network from which obtain the random nodes
    avoid: Set[int]
        Nodes to avoid in the selection
    count: int
        Number of nodes to take
    Returns
    -------
    A random set of nodes from the network, excluding the specified ones.
    """

    viable_nodes = len(network.circuit) - len(avoid)
    assert viable_nodes > count, __NO_VIABLE_NODE_ERROR

    # get a 'count' random available nodes
    return set(random.sample(set(range(len(network.circuit))) - avoid, k=count))


def random_loads(
        network: Network,
        avoid: Set[int],
        count: int = 1,
        resistance_supplier: Callable[[], float] = lambda: random.gauss(1, 2)
) -> Dict[int, float]:
    """
    Generate a map that represents the connection of some loads to a network.

    Parameters
    ----------
    network: Network
        The network from which take the output nodes
    avoid: Set[int]
        Nodes to avoid in the selection
    count: int
        Number of loads to connect
    resistance_supplier: Callable[[], float]
        A function to generate the resistances of the loads
    Returns
    -------
    A map of network node indexes, together with the output load resistance.
    """

    return {
        node: resistance_supplier()
        for node in random_nodes(network, avoid, count)
    }
