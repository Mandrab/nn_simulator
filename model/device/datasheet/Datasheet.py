from dataclasses import dataclass


@dataclass(frozen=True)
class Datasheet:
    """Define the static properties of the device"""

    wires_count: int
    centroid_dispersion: int
    mean_length: float
    std_length: float
    seed: int

    # device size
    Lx: int
    Ly: int

    # update_edge_weights parameters
    kp0: float
    eta_p: int
    kd0: float
    eta_d: int

    # admittance
    Y_min: float
    Y_max: float
