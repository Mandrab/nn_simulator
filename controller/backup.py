import dataclasses
import json
import logging

import networkx as nx

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

    # convert wires dict to correct format
    wires = dict(
        xa=wires['xa'].tolist(),
        ya=wires['ya'].tolist(),
        xc=wires['xc'].tolist(),
        yc=wires['yc'].tolist(),
        xb=wires['xb'].tolist(),
        yb=wires['xa'].tolist(),
        theta=wires['theta'].tolist(),
        avg_length=wires['avg_length'],
        wire_lengths=wires['wire_lengths'].tolist(),
        dispersion=wires['dispersion'],
        centroid_dispersion=wires['centroid_dispersion'],
        gennorm_shape=wires['gennorm_shape'],
        this_seed=wires['this_seed'],
        outside=wires['outside'].tolist(),
        length_x=wires['length_x'],
        length_y=wires['length_y'],
        number_of_wires=wires['number_of_wires'],
        wire_distances=wires['wire_distances'].tolist()
    )

    data = [
        (datasheet_file, dataclasses.asdict(datasheet)),
        (graph_file, nx.node_link_data(graph)),
        (wires_file, wires)
    ]

    # save each data in the file with a json format
    for file_name, data in data:
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
