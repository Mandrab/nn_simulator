from .Datasheet import Datasheet


def from_density(density: float, size: int, wires_length: float) -> Datasheet:
    """Returns a Datasheet that represents a device with a given density."""

    # calculate number of needed wires to reach the density
    wires = int(density * size ** 2 / wires_length ** 2)

    return Datasheet(
        wires_count=wires, Lx=size, Ly=size,
        mean_length=wires_length, std_length=wires_length * 0.35
    )


def from_dict(dictionary: dict) -> Datasheet:
    """Returns a Datasheet from its dict representation."""

    # get a default datasheet
    datasheet = Datasheet()

    # update the default configuration with the data specified in the dictionary
    datasheet.__dict__.update(dictionary)

    return datasheet
