import random

from functools import reduce
from networkx import Graph
from typing import Callable, List, Set


def non_ground_selection(graph: Graph, _: List[int], ground: int) -> Set[int]:
    """Returns non-ground nodes for the mutation"""

    return {*graph.nodes} - {ground}


def minimum_distance_selection(
        outputs: Set[int],
        distance: int
) -> Callable[[Graph, List[int], int], Set[int]]:
    """
    Returns a function the viable nodes selection for the mutation.
    Non-ground nodes and nodes that are 'distance' step near to an output node
    are not selected.
    """

    def _(graph: Graph, _: List[int], ground: int) -> Set[int]:

        # remove ground node from the viable ones
        viable_nodes = {*graph.nodes} - {ground}

        # find nodes 'distance' distant from the output
        def neighbours(node: int, decreased_distance: int) -> Set[int]:

            # base condition: distance 0 is empty set
            if decreased_distance <= 0:
                return set()

            # take distance 1 neighbours
            adjacent_neighbours = {v for k, v in graph.edges(node)}

            # take farther neighbours (neighbours of neighbours)
            neighbours_neighbours = [
                neighbours(node, decreased_distance - 1)
                for node in adjacent_neighbours
            ]

            # reduce to only a set
            neighbours_neighbours = reduce(
                lambda f, s: f | s,
                neighbours_neighbours
            )

            return adjacent_neighbours | neighbours_neighbours

        # take neighbours nodes (and neighbours of neighbours, etc...)
        neighbours = [neighbours(output, distance) for output in outputs]
        neighbours = reduce(lambda f, s: f | s, neighbours)

        return viable_nodes - outputs - neighbours

    return _


def mutate(
        graph: Graph,
        sources: List[int],
        ground: int,
        probability: float,
        minimum_mutants: int,
        maximum_mutants: int,
        viable_node_selection: Callable[[Graph, List[int], int], Set[int]]
) -> List[int]:
    """
    Mutate the input connections of the network in a random way.
    Each source can change, with a fixed probability, between the non-ground
    nodes. Multiple sources can insist on the same node.
    Maximum_mutants must be bigger or equal than minimum_mutants.
    In case no viable node exists, the returned value will be unchanged.
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
    viable_nodes = viable_node_selection(graph, sources, ground)

    # if source change, take a random node != from itself and the ground
    # if source does not change or if there are not viable nodes, return it
    return [
        [*viable_nodes - {s}][random.randrange(len(viable_nodes - {s}))]
        if changes[i] and len(viable_nodes - {s}) > 0 else s
        for i, s in enumerate(sources)
    ]
