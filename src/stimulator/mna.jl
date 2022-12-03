module MNAs

include("./kernels.jl")

using CUDA
using LinearAlgebra
using .Kernels
using ...Devices
using ...Devices.Datasheets

export modified_voltage_node_analysis!

""" Override default `similar` symbol with a custom approx function. """
≈(a::AbstractFloat, b::AbstractFloat) = isapprox(a, b; atol=eps(Float32), rtol=0)

""" Override default `not-similar` symbol with a custom approx function. """
≉(a::AbstractFloat, b::AbstractFloat) = ! isapprox(a, b; atol=eps(Float32), rtol=0)

"""
Perform the Modified Nodal Analysis to calculate the voltage distribution.

# Parameters:
- `device::Device`: The device/network to which calculate the voltage distribution.
- `inputs::Vector{Float64}`: The voltage values of the network wires.
  If the value is 0, the wire is not an input / fixed voltage node, and vice-versa.
"""
function modified_voltage_node_analysis!(device::Device, inputs::Vector{Float64})

    # create a vector to contain the voltages of the input nodes
    # the ground nodes are not present
    V = zeros(Float32, length(device.V))
    append!(V, collect(map(Float32, filter(v -> v ≉ .0, inputs))))

    # create a vector to identify the sources (1: source, 0: non-source)
    # each column contains only one '1': there is 1 column for each source
    M = CUDA.zeros(Float32, length(V), length(V))

    # enumerate the inputs only (used to define
    # their position on bottom and right of M)
    counter = Iterators.Stateful(1:length(inputs))
    inputs = CuArray(map(v -> v ≈ .0 ? 0 : popfirst!(counter), inputs))

    # compile kernel without running it
    kernel = @cuda launch=false kernel!(M, device.G, inputs)

    # calculate the optimal number of threads and blocks
    threads, blocks = optimize(kernel, M)

    # run the kernel with the optimized configuration
    kernel(
        # data parameters
        M, device.G, inputs;

        # configuration parameters
        threads, blocks
    )

    # analyze the circuit (Yx = z -> x = Y^(-1)z)
    device.V = M \ CuArray(V)
end

"""
Kernel for the modified nodal analysis.

# Parameters:
- `M::CuMatrix`: Support matrix used for the MNA.
- `G::CuMatrix`: Conductance matrix of the device.
- `inputs::CuArray`: An array representing the input wires.
  The 0 means that the wires at this index is not and input,
  A different incremental number represents a source/input wire
  and its relative index.
"""
function kernel!(M, G, inputs)
    i = threadIdx().x + (blockIdx().x - 1) * blockDim().x
    j = threadIdx().y + (blockIdx().y - 1) * blockDim().y

    # exit in case of overflow or
    # if the address is on the diagonal
    width, height = size(M)
    if i == j || i > width || j > height
        return
    end

    # check if we are in the central part of M:
    # the MNA requires to negate the conductance
    # and to store their sum in the diagonal nodes
    width, height = size(G)
    if i <= width && j <= height

        # check if there is a junction
        if (c = G[i, j]) ≉ .0
            M[i, j] = -c
            CUDA.@atomic M[i, i] += c
        end

    # check if we are on the right of M
    elseif i <= length(inputs) && j == width + inputs[i]

        # if 'i' identifies an input set it in M
        if inputs[i] != 0
            M[i, j] = 1
        end

    # check if we may be on the bottom of M
    elseif j <= length(inputs) && i == height + inputs[j]

        # if 'i' identifies an input set it in M
        if inputs[j] != 0
            M[i, j] = 1
        end

    end

    return
end

end
