import dataclasses
import json
import networkx as nx
import numpy as np

from nn_simulator.logger import logger
from nn_simulator.model.device import Datasheet
from nn_simulator.model.device.datasheet import factory
from nn_simulator.model.device.network import Network
from nn_simulator.model.device.networks import nn2nx, nx2nn
from os.path import exists as e
from typing import Dict, Iterable, Any, Tuple

__DATASHEET_FILE = "datasheet.dat"
__GRAPH_FILE = "graph.dat"
__WIRES_FILE = "wires.dat"
__CONNECTIONS_FILE = "connections.dat"


def save(
        datasheet: Datasheet,
        network: Network,
        wires: Dict,
        connections: Dict,
        datasheet_file: str = __DATASHEET_FILE,
        graph_file: str = __GRAPH_FILE,
        wires_file: str = __WIRES_FILE,
        connections_file: str = __CONNECTIONS_FILE
):
    """
    Save the datasheet, graph, wires and connections to file.

    Parameters
    ----------
    datasheet: Datasheet
        The technical representation of the network
    network: Network
        Simulation of the physical network
    wires: Dict
        Network definition support
    connections: Dict
        Map of transducers name and input node
    datasheet_file: str
        Name of the file where to save the datasheet
    graph_file: str
        Name of the file where to save the graph
    wires_file: str
        Name of the file where to save the wires
    connections_file: str
        Name of the file where to save the connections
    """

    logger.info("Saving graph to file")

    # remove a saved instance of the graph from the wires-dict
    if 'G' in wires:
        del wires['G']

    # convert wires dict to correct format
    wires = dict([
        (key, value) if not isinstance(value, np.ndarray)
        else (key, value.tolist())
        for key, value in wires.items()
    ])

    pairs = [
        (datasheet_file, dataclasses.asdict(datasheet)),
        (graph_file, nx.node_link_data(nn2nx(network))),
        (wires_file, wires),
        (connections_file, connections)
    ]

    # save each data in the file with a json format
    for file_name, data in pairs:
        with open(file_name, 'w') as file:
            json.dump(data, file)


def exist(
        datasheet_file: str = __DATASHEET_FILE,
        graph_file: str = __GRAPH_FILE,
        wires_file: str = __WIRES_FILE,
        connections_file: str = __CONNECTIONS_FILE
) -> Iterable[bool]:
    """
    Check if graph, datasheet and wires files exists.

    Parameters
    ----------
    datasheet_file: str
        Name of the datasheet file
    graph_file: str
        Name of the graph file
    wires_file: str
        Name of the wires file
    connections_file: str
        Name of the connections file

    Returns
    -------
    An sequence of boolean representing existence (True) or not (False)
    """

    return map(e, (graph_file, datasheet_file, wires_file, connections_file))


def read(
        datasheet_file: str = __DATASHEET_FILE,
        graph_file: str = __GRAPH_FILE,
        wires_file: str = __WIRES_FILE,
        connections_file: str = __CONNECTIONS_FILE
) -> Tuple[Network, Datasheet, Dict[str, Any], Dict[str, int]]:
    """
    Read graph, datasheet and wires from the files and import them.

    Parameters
    ----------
    datasheet_file: str
        Name of the datasheet file
    graph_file: str
        Name of the graph file
    wires_file: str
        Name of the wires file
    connections_file: str
        Name of the connections file

    Returns
    -------
    A tuple containing the network, datasheet, wires and connections.
    """

    logger.info("Importing graph from file")

    # load and convert the json to a datasheet
    with open(datasheet_file, 'r') as file:
        text = json.load(file)
        datasheet = factory.from_dict(text)

    # load and convert the json to a graph
    with open(graph_file, 'r') as file:
        text = json.load(file)
        graph = nx.node_link_graph(text)
        network = nx2nn(graph)

    # load and convert the json to a wires dict
    with open(wires_file, 'r') as file:
        wires = json.load(file)
        wires = dict([
            (key, value) if not isinstance(value, list)
            else (key, np.asarray(value, dtype=np.float32))
            for key, value in wires.items()
        ])

    # load and convert the json to a wires dict
    with open(connections_file, 'r') as file:
        connections = json.load(file)

    # build the graph and return it
    return network, datasheet, wires, connections
