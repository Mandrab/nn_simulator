import networkx as nx

from functools import cache
from collections.abc import Iterable
from networkx import Graph

from model.analysis.utils import calculate_currents
from model.device.datasheet.Datasheet import Datasheet


class Evolution:
    """Contains the evolution/history of the network"""

    network_instances: [Graph] = []  # contains the evolution in time of the net

    def __init__(
            self,
            datasheet: Datasheet,
            wires_dict: dict,
            ground: int,
            delta_time: float
    ):
        self.datasheet = datasheet
        self.wires_dict = wires_dict
        self.ground = ground
        self.delta_t = delta_time

    def append(self, graph: Graph, stimulus: [(int, float)]):
        """Add a graph (i.e., network state) to the history"""

        self.network_instances.append((graph.copy(), stimulus))

    @cache
    def currents_graphs(self, reverse=False) -> Iterable[Graph]:
        """Get currents flow in the graphs. Apply in a lazy way"""

        graphs = [g for g, _ in self.network_instances]

        if reverse:
            graphs = reversed(graphs)

        return map(calculate_currents, graphs)

    def information_centrality(self):
        """Return information centrality measure for the network evolution"""

        graphs = [(g, calculate_currents(g)) for g, _ in self.network_instances]

        for m, h in graphs:
            nx.set_node_attributes(
                h,
                nx.information_centrality(m, weight='Y'),
                'information_centrality'
            )

        return [h for m, h in graphs]

    @property
    def graph(self) -> Graph:
        """Returns the most updated graph in the history"""

        return self.network_instances[-1][0]

    @property
    def inputs(self) -> [(int, float)]:
        """Return the latest stimulation values"""

        return self.network_instances[-1][1]
