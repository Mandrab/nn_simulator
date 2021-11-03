from dataclasses import dataclass


@dataclass
class Datasheet:
    wires_count: int
    centroid_dispersion: int
    mean_length: float
    std_length: float
    seed: int

    # todo constant?
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
