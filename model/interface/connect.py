from networkx import Graph


def connect(graph: Graph, output: int, resistance: float) -> int:
    """
    Connect a device to the selected output node.
    The device is represented by an edge with a specific resistance and it is
    connected to a newly added ground.
    The ground is finally returned.
    """

    # generate a ground id and add it to the graph
    ground = graph.number_of_nodes()
    graph.add_node(ground)
    graph.nodes[ground]['V'] = 0

    # add a weighted edge between output and ground
    graph.add_edge(output, ground)
    graph[output][ground]['Y'] = 1 / resistance

    return ground
