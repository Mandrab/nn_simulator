import cupy as cp
import networkx as nx

from nn_simulator.model.analysis.utils import calculate_currents
from nn_simulator.model.device import Datasheet
from nn_simulator.model.device.network import Network as Nw, copy
from nn_simulator.model.device.networks import nn2nx
from dataclasses import dataclass, field
from functools import cached_property
from collections.abc import Iterable, Generator
from typing import Set, Tuple, List, Dict


@dataclass
class Evolution:
    """
    Contains the evolution/history of the network.

    Parameters
    ----------
    datasheet: Datasheet
        Datasheet of the stimulated device
    wires_dict: Dict
        Wires dictionary of the device
    delta_time: float
        Network stimulation delay
    loads: Dict[int, float]
        Node connection index (int) and resistance (float) of external loads.
        May be empty if the simulation does not include loads
    network_instances: List[Tuple[NN, List[Tuple[int, float]]]]
        Contains the sequence of networks representing the evolution in time
    """

    datasheet: Datasheet
    wires_dict: Dict
    delta_time: float
    loads: Dict[int, float] = field(default_factory=dict)
    instances: List[Tuple[Nw, Dict[int, float]]] = field(default_factory=list)

    def append(self, graph: Nw, stimulus: Dict[int, float]):
        """
        Add a network (i.e., network state) to the history. The instance is
        copied before being add.

        Parameters
        ----------
        graph: Network
            The network to add to the history
        stimulus: Iterable[Tuple[int, float]]
            The map of node-index and input signal to the network at the given
            instant
        """

        self.instances.append((copy(graph.device), stimulus))

    def currents_graphs(self, reverse: bool = False) -> Generator[Nw]:
        """
        Save the matrix of the currents flowing in the circuit to a given
        instance. It is calculated in a lazy way.

        Parameters
        ----------
        reverse: bool
            True if the instances should be returned according to increasing
            times. False otherwise
        Returns
        -------
        A lazy generator of the sequence of Network instances containing the
        current matrix.
        """

        graphs = reversed(self.instances) if reverse else self.instances

        def result():
            for n, _ in graphs:
                n.currents = calculate_currents(n)
                yield n
        return result()

    def information_centrality(
            self, reverse: bool = False
    ) -> Iterable[cp.ndarray]:
        """
        Return information centrality measure for the network evolution.

        Parameters
        ----------
        reverse: bool
            True if the instances should be returned according to increasing
            times. False otherwise
        Returns
        -------
        A sequence of matrix containing the information centrality of each wire.
        """

        graphs = [g for g, _ in self.instances]

        if reverse:
            graphs = reversed(graphs)

        def _(network: Nw) -> cp.ndarray:
            centrality = nx.information_centrality(nn2nx(network), weight='Y')
            return cp.asarray(list(centrality.values()), dtype=cp.float32)

        return map(_, graphs)

    @property
    def graph(self) -> Nw: return self.instances[-1][0]

    @property
    def inputs(self) -> Dict[int, float]: return self.instances[-1][1]

    @property
    def sources(self) -> Set[int]: return set(self.inputs)

    @cached_property
    def duration(self): return range(len(self.instances))

    @cached_property
    def update_times(self): return [x * self.delta_time for x in self.duration]
