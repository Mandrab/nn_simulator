import random

from networkx import Graph


def mutate(
        graph: Graph,
        sources: [int],
        ground: int,
        probability: float,
        minimum_mutants: int,
        maximum_mutants: int
) -> [int]:
    """
    Mutate the input connections of the network in a random way.
    Each source can change, with a fixed probability, between the non-ground
    nodes. Multiple sources can insist on the same node.
    Maximum_mutants must be bigger or equal than minimum_mutants.
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

    # select viable alternative nodes (i.e., not ground)
    viable_nodes = {*graph.nodes} - {ground}

    # if source change, take a random node != from itself and the ground
    # if source does not change return it
    return [
        [*viable_nodes - {source}][random.randint(0, len(viable_nodes) - 1)]
        if changes[idx] else source
        for idx, source in enumerate(sources)
    ]
