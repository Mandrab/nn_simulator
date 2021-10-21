from dataclasses import dataclass


@dataclass
class Device():
    wires_count: int
    centroid_dispersion: int

    mean_length: float
    std_length: float
    seed: int

    # todo non constant
    Lx: int
    Ly: int

    # source and ground node positions
    sourcenode: int
    groundnode: int

    # update_edge_weights parameters
    kp0: float
    eta_p: int
    kd0: float
    eta_d: int

    # admittance
    Y_min: float
    Y_max: float
