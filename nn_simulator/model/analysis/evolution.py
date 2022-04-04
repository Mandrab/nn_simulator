import cupy as cp
import networkx as nx

from ..device.networks import nn2nx
from .utils import calculate_currents
from nn_simulator.model.device import Datasheet
from nn_simulator.model.device.network import Network as Nw, copy
from dataclasses import dataclass, field
from functools import cached_property
from collections.abc import Iterable, Generator
from typing import Set, Tuple, List, Dict


@dataclass
class Evolution:
    """
    Contains the evolution/history of the network

    Parameters
    ----------
    datasheet: Datasheet
        datasheet of the stimulated device
    wires_dict: Dict
        wires dictionary of the device
    delta_time: float
        network stimulation delay
    grounds: Set[int]
        list of nodes directly connected to ground.
        may be empty if the grounds are serial to the loads:
        Source --- [chip] --- Load --- Ground
    loads: Set[Tuple[int, float]]
        list of nodes on which there are external loads attached.
        may be empty if the simulation does not include loads
        the integer is the node identifier, the float the load resistance
    network_instances: List[Tuple[NN, List[Tuple[int, float]]]]
        contains the evolution in time of the network
    """

    datasheet: Datasheet
    wires_dict: Dict
    delta_time: float
    grounds: Set[int] = field(default_factory=set)
    loads: Set[Tuple[int, float]] = field(default_factory=set)
    instances: List[Tuple[Nw, Dict[int, float]]] = field(default_factory=list)

    def append(self, graph: Nw, stimulus: [(int, float)]):
        """
        Add a graph (i.e., network state) to the history.
        The graph is copied before being add.
        """

        self.instances.append((copy(graph.device), dict(stimulus)))

    def currents_graphs(self, reverse: bool = False) -> Generator:
        """Get currents flow in the graphs. Apply in a lazy way"""

        graphs = reversed(self.instances) if reverse else self.instances

        def result():
            for n, _ in graphs:
                n.currents = calculate_currents(n)
                yield n
        return result()

    def information_centrality(
            self, reverse: bool = False
    ) -> Iterable[cp.ndarray]:
        """Return information centrality measure for the network evolution"""

        graphs = [g for g, _ in self.instances]

        if reverse:
            graphs = reversed(graphs)

        def _(network: Nw) -> cp.ndarray:
            centrality = nx.information_centrality(nn2nx(network), weight='Y')
            return cp.asarray(list(centrality.values()), dtype=cp.float32)

        return map(_, graphs)

    @property
    def graph(self) -> Nw:
        """Returns the most updated graph in the history"""

        return self.instances[-1][0]

    @property
    def inputs(self) -> Dict[int, float]:
        """Return the latest stimulation values"""

        return self.instances[-1][1]

    @property
    def sources(self) -> Set[int]:
        """Return the latest stimulation values"""

        return {s for s, _ in self.inputs.items()}

    @cached_property
    def duration(self):
        """Return the time elapsed between the first and last update"""

        return range(len(self.instances))

    @cached_property
    def update_times(self):
        """Return the sequence of update times of the simulation"""

        return [x * self.delta_time for x in self.duration]
