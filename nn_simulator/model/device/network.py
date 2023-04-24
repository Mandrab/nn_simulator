from __future__ import annotations

import numpy as np

from dataclasses import dataclass
from typing import Tuple


@dataclass
class Network:
    """
    Contains the state of the nanowire network.

    Fields
    ------
    adjacency: np.ndarray
        adjacency (i.e., connections) matrix of the device
    wires_position: Tuple[np.ndarray, np.ndarray]
        x and y position of the wires
    junctions_position: Tuple[np.ndarray, np.ndarray]
        x and y position of the wires junctions
    circuit: np.ndarray
        adjacency matrix with conductances instead of 1s
    admittance: np.ndarray
        admittance matrix for the junction resistance update
    voltage: np.ndarray
        voltages of the circuit nodes
    grounds: int
        specify the number of nodes to be considered ground (those have to be at
        the rightmost part of the matrix)
    """

    adjacency: np.ndarray
    wires_position: Tuple[np.ndarray, np.ndarray]
    junctions_position: Tuple[np.ndarray, np.ndarray]

    circuit: np.ndarray
    admittance: np.ndarray
    voltage: np.ndarray

    device_grounds: int = 0
    external_grounds: int = 0

    @property
    def device(self) -> Network:
        """
        Generate a network instance as a view on the original one, excluding the
        external connections to grounds. If no external connections are present,
        the same instance is returned.

        Returns
        -------
        A reduced view on the same network that excludes the grounds.
        """
        if not self.external_grounds:
            return self
        return Network(
            self.adjacency[:-self.external_grounds, :-self.external_grounds],
            self.wires_position, self.junctions_position,
            self.circuit[:-self.external_grounds, :-self.external_grounds],
            self.admittance[:-self.external_grounds, :-self.external_grounds],
            self.voltage[:-self.external_grounds],
            self.device_grounds, external_grounds=0
        )

    @property
    def nodes(self) -> int:
        """
        Returns the number of nodes composing the circuit, including grounds.

        Returns
        -------
        An integer representing the number of different nodes of the circuit:
            # wires + # grounds
        """
        return len(self.adjacency)

    @property
    def wires(self) -> int:
        """
        Returns the number of wires composing the circuit, excluding grounds.

        Returns
        -------
        An integer representing the number of different wires of the circuit.
        """
        return self.nodes - self.grounds

    @property
    def grounds(self) -> int:
        """
        Returns the number of grounds connected to the circuit.

        Returns
        -------
        An integer representing the number of grounds connected to the circuit.
        """
        return self.device_grounds + self.external_grounds


def copy(network: Network) -> Network:
    """
    Makes a deep copy of the nanowire network.

    Parameters
    ----------
    network: Network
        the network to copy
    Returns
    -------
    A copy of the input nanowire network.
    """
    xw, yw = network.wires_position
    xj, yj = network.junctions_position

    adj = network.adjacency if ram else network.adjacency.copy()
    wp = (xw.copy(), yw.copy())
    jp = (xj.copy(), yj.copy())
    circuit = network.circuit.copy()
    adm = network.admittance.copy()
    voltage = network.voltage.copy()

    d_grounds, e_grounds = network.device_grounds, network.external_grounds
    return Network(adj, wp, jp, circuit, adm, voltage, d_grounds, e_grounds)
