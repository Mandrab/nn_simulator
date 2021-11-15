import dataclasses
import json
import logging

import networkx as nx
import numpy as np

from model.device.datasheet.Datasheet import Datasheet
from model.device.datasheet.factory import from_dict
from networkx import Graph
from os.path import exists

__DATASHEET_FILE = "datasheet.dat"
__GRAPH_FILE = "graph.dat"
__WIRES_FILE = "wires.dat"


def save(
        datasheet: Datasheet,
        graph: Graph,
        wires: dict,
        datasheet_file: str = __DATASHEET_FILE,
        graph_file: str = __GRAPH_FILE,
        wires_file: str = __WIRES_FILE
):
    """Save the graph, datasheet and wires to files"""

    logging.info("Saving graph to file")

    # remove a saved instance of the graph from the wires-dict
    del wires['G']

    # convert wires dict to correct format
    wires = dict([
        (key, value) if not isinstance(value, np.ndarray)
        else (key, value.tolist())
        for key, value in wires.items()
    ])

    pairs = [
        (datasheet_file, dataclasses.asdict(datasheet)),
        (graph_file, nx.node_link_data(graph)),
        (wires_file, wires)
    ]

    # save each data in the file with a json format
    for file_name, data in pairs:
        with open(file_name, 'w') as file:
            json.dump(data, file)


def exist(
        datasheet_file: str = __DATASHEET_FILE,
        graph_file: str = __GRAPH_FILE,
        wires_file: str = __WIRES_FILE
) -> (bool, bool):
    """Check if graph, datasheet and wires files exists"""

    return exists(graph_file), exists(datasheet_file), exists(wires_file)


def read(
        datasheet_file: str = __DATASHEET_FILE,
        graph_file: str = __GRAPH_FILE,
        wires_file: str = __WIRES_FILE
) -> (Graph, dict):
    """Read graph, datasheet and wires from the files and import them"""

    logging.info("Importing graph from file")

    # load and convert the json to a datasheet
    with open(datasheet_file, 'r') as file:
        text = json.load(file)
        datasheet = from_dict(text)

    # load and convert the json to a graph
    with open(graph_file, 'r') as file:
        text = json.load(file)
        graph = nx.node_link_graph(text)

    # load and convert the json to a wires dict
    with open(wires_file, 'r') as file:
        wires = json.load(file)

    # build the graph and return it
    return graph, datasheet, wires
