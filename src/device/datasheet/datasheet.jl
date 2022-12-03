using Parameters

export Datasheet

"""
Define the static properties of the device.

# Fields:
- `wires_count::Int64`: Total number of wires in the network.
- `wires_length_mean::Float64`: Average wire length in µm.
- `wires_length_variance::Float64`: Length of the nano-wire in µm.
- `size::Int64`: Length of one side of the device package in µm.
- `kp:Float32`: One of the junction potentiation coefficient.
- `eta_p::Int64`: One of the junction potentiation coefficient.
- `kd::Float32`: One of the junction depression coefficient.
- `eta_d::Int64`: One of the junction depression coefficient.
- `Y_min::Float32`: Minimum admittance value.
- `Y_max::Float32`: Maximum admittance value.
- `seed::Int64`: Seed of the random number generator to create reproducible networks.
"""
@with_kw struct Datasheet
    # wires data
    wires_count::Int64 = 1500
    wires_length_mean::Float64 = 40.0
    wires_length_variance::Float64 = 14.0

    # device package size
    size::Int64 = 500

    # update_edge_weights parameters
    kp::Float32 = 0.0001f0
    eta_p::Int64 = 10
    kd::Float32 = 0.5f0
    eta_d::Int64 = 1

    # admittance ranges
    Y_min::Float32 = 0.001f0
    Y_max::Float32 = 0.001f0 * 100

    # random number generator seed
    seed::Int64 = 40
end
