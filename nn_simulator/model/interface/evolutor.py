import numpy as np
import random

from nn_simulator.model.device.network import Network
from typing import Callable, List, Set


def non_ground_selection(network: Network) -> Set[int]:
    """
    Returns non-ground nodes for the mutation.

    Parameters
    ----------
    network: Network
        The network from which take the nodes
    Returns
    -------
    A set of non-ground nodes.
    """

    return set(range(network.wires))


def minimum_distance_selection(
        outputs: List[int],
        distance: int = 0,
        negate: bool = False
) -> Callable[[Network, List[int]], Set[int]]:
    """
    Returns a function for the viable nodes selection for the mutation.
    Ground nodes and nodes that are 'distance'-step near to an output node
    are not selected.

    Parameters
    ----------
    outputs: List[int]
        Indexes of output nodes (the ones that we have to be far from)
    distance: int
        Minimum distance from an output to be considered a viable node
    negate: bool
        If True, the function is `negated` and the returned nodes are the
        grounds, outputs and neighbor. If it is False, the returned node are the
        others.
    Returns
    -------
    A function that calculates the viable nodes to be selected in a network. It
    takes the Network as input, as well as another value. That is not needed in
    this logic, and only exists to personalise more similar functions,
    maintaining a template of the parameter types.
    """

    def _(network: Network, _: List[int]) -> Set[int]:

        # create a mask of viable nodes (false = viable; initially all)
        viable = np.zeros(network.nodes - network.external_grounds, dtype=bool)

        # set unavailable (i.e., true) the specified nodes
        viable[outputs] = True

        # find nodes 'distance' distant from the output
        def neighbours(mask: np.ndarray, decreased_distance: int) -> np.ndarray:

            # base condition: distance 0 is empty set
            if decreased_distance <= 0:
                return mask

            # set the nodes neighbor as unavailable
            mask |= np.sum(network.adjacency[mask], axis=0, dtype=bool)

            # recur until found all neighbours
            return neighbours(mask, decreased_distance - 1)

        # set unavailable the nodes neighbours
        viable = neighbours(viable, distance)

        # negate the boolean values if required
        if not negate:
            viable = np.logical_not(viable)

        # remove device grounds from list of available nodes
        if network.device_grounds > 0:
            viable = viable[:-network.device_grounds]

        # retrieve nodes indexes
        return {i for i, v in enumerate(viable) if v}

    return _


def mutate(
        network: Network,
        sources: List[int],
        probability: float,
        minimum_mutants: int,
        maximum_mutants: int,
        viable_node_selection: Callable[[Network, List[int]], Set[int]]
) -> List[int]:
    """
    Mutate the input connections of the network in a random way. Each source can
    change, with a fixed probability, between the non-ground nodes. Multiple
    sources can insist on the same node. Maximum_mutants must be bigger or equal
    than minimum_mutants. In case no viable node exists, the returned value will
    be unchanged.

    Parameters
    ----------
    network: Network
        The network in which mutate the connections
    sources: List[int]
        The source node to reconnect
    probability: float
        Probability to mute one connection
    minimum_mutants: int
        Minimum number of inputs to reconnect, if possible
    maximum_mutants: int
        Maximum number of inputs to reconnect, if possible
    viable_node_selection: Callable[[Network, List[int]], Set[int]]
        Function to select viable nodes for the replacement/reconnection. It
        must accept the network and a list of actual sources
    Returns
    -------
    A list with the new nodes connection indexes for each source.
    """

    # determine if a node should mutate or not
    changes = [random.random() < probability for _ in sources]

    def change_mutants_number(variation: int):

        # if variation is positive add mutants, otherwise remove them
        increase = variation > 0

        # get index of nodes that may be forced
        selected = [
            idx for idx, mute in enumerate(changes)
            # increase true -> take non-changing elements (false)
            # increase false -> take changing elements (true)
            if mute != increase
        ]

        # selected random forcible-sources and force their mutation
        for idx in random.sample(selected, abs(variation)):
            # increase true -> set change true, otherwise set false
            changes[idx] = increase

    # count how many sources will be changed
    mutants_count = sum(changes)

    # if not enough mutants get more
    if mutants_count < minimum_mutants:
        change_mutants_number(minimum_mutants - mutants_count)

    # if too many mutants discard some
    elif mutants_count > maximum_mutants:
        change_mutants_number(maximum_mutants - mutants_count)

    # select viable alternative nodes
    viable_nodes = viable_node_selection(network, sources)

    # if source change, take a random node != from itself and the ground
    # if source does not change or if there are not viable nodes, return it
    return [
        [*viable_nodes - {s}][random.randrange(len(viable_nodes - {s}))]
        if changes[i] and len(viable_nodes - {s}) > 0 else s
        for i, s in enumerate(sources)
    ]
