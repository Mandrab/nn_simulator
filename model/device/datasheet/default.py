from model.device.datasheet.Datasheet import Datasheet

default = Datasheet(
    wires_count=1500,
    centroid_dispersion=200,
    mean_length=40.0,
    std_length=14.0,
    seed=40,
    Lx=500,
    Ly=500,
    kp0=0.0001,
    eta_p=10,
    kd0=0.5,
    eta_d=1,
    Y_min=0.001,
    Y_max=0.001 * 100
)
