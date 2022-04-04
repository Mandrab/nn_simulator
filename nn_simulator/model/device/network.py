from __future__ import annotations

import cupy as cp

from dataclasses import dataclass
from typing import Tuple


@dataclass
class Network:
    """
    Contains the state of the nanowire network.

    Fields
    ------
    adjacency: cp.ndarray
        adjacency (i.e., connections) matrix of the device
    wires_position: Tuple[cp.ndarray, cp.ndarray]
        x and y position of the wires
    junctions_position: Tuple[cp.ndarray, cp.ndarray]
        x and y position of the wires junctions
    circuit: cp.ndarray
        adjacency matrix with conductances instead of 1s
    admittance: cp.ndarray
        admittance matrix for the junction resistance update
    voltage: cp.ndarray
        voltages of the circuit nodes
    grounds: int
        specify the number of nodes to be considered ground (those have to be at
        the rightmost part of the matrix)
    """

    adjacency: cp.ndarray
    wires_position: Tuple[cp.ndarray, cp.ndarray]
    junctions_position: Tuple[cp.ndarray, cp.ndarray]

    circuit: cp.ndarray
    admittance: cp.ndarray
    voltage: cp.ndarray

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


def copy(network: Network, ram: bool = True) -> Network:
    """
    Makes a deep copy of the nanowire network.

    Parameters
    ----------
    network: Network
        the network to copy
    ram: bool
        specify if the copied system should remain in the gpu memory or be moved
        to the RAM
    Returns
    -------
    A copy of the input nanowire network.
    """
    xw, yw = network.wires_position
    xj, yj = network.junctions_position

    adj = cp.asnumpy(network.adjacency) if ram else network.adjacency.copy()
    wp = (
        cp.asnumpy(xw) if ram else xw.copy(),
        cp.asnumpy(yw) if ram else yw.copy()
    )
    jp = (
        cp.asnumpy(xj) if ram else xj.copy(),
        cp.asnumpy(yj) if ram else yj.copy()
    )
    circuit = cp.asnumpy(network.circuit) if ram else network.circuit.copy()
    adm = cp.asnumpy(network.admittance) if ram else network.admittance.copy()
    voltage = cp.asnumpy(network.voltage) if ram else network.voltage.copy()

    d_grounds, e_grounds = network.device_grounds, network.external_grounds
    return Network(adj, wp, jp, circuit, adm, voltage, d_grounds, e_grounds)
