using Parameters

export Datasheet

"""
Define the static properties of the device.

# Fields:
- `wires_count::Integer`: Total number of wires in the network.
- `wires_length_mean::AbstractFloat`: Average wire length in µm.
- `wires_length_variance::AbstractFloat`: Length of the nano-wire in µm.
- `size::Integer`: Length of one side of the device package in µm.
- `kp:AbstractFloat`: One of the junction potentiation coefficient.
- `eta_p::Integer`: One of the junction potentiation coefficient.
- `kd::AbstractFloat`: One of the junction depression coefficient.
- `eta_d::Integer`: One of the junction depression coefficient.
- `Y_min::AbstractFloat`: Minimum admittance value.
- `Y_max::AbstractFloat`: Maximum admittance value.
- `seed::Integer`: Seed of the random number generator to create reproducible networks.
"""
@with_kw struct Datasheet
    # wires data
    wires_count::Integer = 1500
    wires_length_mean::AbstractFloat = 40.0
    wires_length_variance::AbstractFloat = 14.0

    # device package size
    size::Integer = 500

    # update_edge_weights parameters
    kp::AbstractFloat = 0.0001
    eta_p::Integer = 10
    kd::AbstractFloat = 0.5
    eta_d::Integer = 1

    # admittance ranges
    Y_min::AbstractFloat = 0.001
    Y_max::AbstractFloat = 0.001 * 100

    # random number generator seed
    seed::Integer = 40
end
