using CUDA

export Device

Indexes = Pair{Int64, Int64}
Point = Pair{Float64, Float64}
Wire = Tuple{
    Point,  # centroid
    Point,  # start
    Point,  # end
    Float64 # length
}

"""
Contains the state of the nanowire network.

# Fields:
- `wires::Vector{Wire}`: Set of wires and their own information.
- `junctions::Dict{Indexes, Point}`: Set of wires junctions and their position.
- `A::CuArray{Bool, 2}`: Adjacency matrix (i.e., junctions) of the device.
- `G::CuArray{Float64}`: Adjacency matrix with the value of the conductance in each junction.
- `Y::CuArray{Float64}`: Adjacency matrix with the value of the admittance in each junction.
- `V::CuArray{Float64}`: Potential (i.e., voltage) of each wire.
- `grounds::Integer`: Number of nodes to be considered ground (in the rightmost part of the matrix).
"""
mutable struct Device
    wires::Vector{Wire}

    junctions::Dict{Indexes, Point}

    A::CuArray{Bool, 2}
    G::CuArray{Float64}
    Y::CuArray{Float64}
    V::CuArray{Float64}

    grounds::Integer
end
