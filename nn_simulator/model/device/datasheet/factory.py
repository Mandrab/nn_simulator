from nn_simulator.model.device.datasheet.Datasheet import Datasheet
from typing import Dict


def from_density(
        density: float,
        size: int,
        wires_length: float,
        seed: int = Datasheet.seed
) -> Datasheet:
    """
    Returns a Datasheet that represents a device with a given density.

    Parameters
    ----------
    density: float
        Desired network density
    size: int
        Device package size (micro-meter)
    wires_length: float
        Length of a single nanowire (micro-meter)
    seed: int
        Generation seed

    Returns
    -------
    The datasheet of a device respecting the specified constraints.
    """

    # calculate number of needed wires to reach the density
    wires = int(density * size ** 2 / wires_length ** 2)

    return Datasheet(
        wires_count=wires, Lx=size, Ly=size,
        mean_length=wires_length, std_length=wires_length * 0.35,
        seed=seed
    )


def from_dict(dictionary: Dict) -> Datasheet:
    """
    Returns a Datasheet from its dict representation.

    Parameters
    ----------
    dictionary: Dict
        The dictionary representation of the datasheet
    Returns
    -------
    The datasheet of a device respecting the constraints specified in the
    dictionary.
    """

    # get a default datasheet
    datasheet = Datasheet()

    # update the default configuration with the data specified in the dictionary
    datasheet.__dict__.update(dictionary)

    return datasheet
