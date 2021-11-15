import networkx as nx

from dataclasses import dataclass, field
from functools import cached_property
from collections.abc import Iterable
from networkx import Graph
from typing import Set, Tuple, List
from model.analysis.utils import calculate_currents
from model.device.datasheet.Datasheet import Datasheet


@dataclass
class Evolution:
    """Contains the evolution/history of the network"""

    # datasheet of the stimulated device
    datasheet: Datasheet

    # wires dictionary of the device
    wires_dict: dict

    # network stimulation delay
    delta_time: float

    # list of nodes directly connected to ground.
    # may be empty if the grounds are serial to the loads:
    #   Source --- [chip] --- Load --- Ground
    grounds: Set[int] = field(default_factory=set)

    # list of nodes on which there are external loads attached.
    # may be empty if the simulation does not include loads
    # the integer is the node identifier, the float the load resistance
    loads: Set[Tuple[int, float]] = field(default_factory=set)

    # contains the evolution in time of the network
    network_instances: List[Tuple[Graph, List[Tuple[int, float]]]] =\
        field(default_factory=list)

    def append(self, graph: Graph, stimulus: [(int, float)]):
        """
        Add a graph (i.e., network state) to the history.
        The graph is copied before being add.
        """

        self.network_instances.append((graph.copy(), stimulus))

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
    def inputs(self) -> List[Tuple[int, float]]:
        """Return the latest stimulation values"""

        return self.network_instances[-1][1]

    @property
    def sources(self) -> Set[int]:
        """Return the latest stimulation values"""

        return {s for s, _ in self.network_instances[-1][1]}

    @cached_property
    def duration(self):
        """Return the time elapsed between the first and last update"""

        return range(len(self.network_instances))

    @cached_property
    def update_times(self):
        """Return the sequence of update times of the simulation"""

        return [x * self.delta_time for x in self.duration]
