from .Datasheet import Datasheet


def from_dict(dictionary: dict) -> Datasheet:
    """Return a Datasheet from its dict representation"""

    datasheet = Datasheet()

    datasheet.__dict__.update(dictionary)

    return datasheet
