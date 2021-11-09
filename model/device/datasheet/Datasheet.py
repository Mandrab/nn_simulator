from dataclasses import dataclass


@dataclass(frozen=True)
class Datasheet:
    """Define the static properties of the device"""

    wires_count: int = 1500
    centroid_dispersion: int = 200
    mean_length: float = 40.0
    std_length: float = 14.0
    seed: int = 40

    # device size
    Lx: int = 500
    Ly: int = 500

    # update_edge_weights parameters
    kp0: float = 0.0001
    eta_p: int = 10
    kd0: float = 0.5
    eta_d: int = 1

    # admittance
    Y_min: float = 0.001
    Y_max: float = 0.001 * 100


default = Datasheet
