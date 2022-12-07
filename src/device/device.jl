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
- `A::AbstractMatrix{Bool}`: Adjacency matrix (i.e., junctions) of the device.
- `G::AbstractMatrix{Float32}`: Adjacency matrix with the value of the conductance in each junction.
- `Y::AbstractMatrix{Float32}`: Adjacency matrix with the value of the admittance in each junction.
- `V::AbstractVector{Float32}`: Potential (i.e., voltage) of each wire.
- `grounds::Int64`: Number of nodes to be considered ground (in the rightmost part of the matrix).
"""
mutable struct Device{
        BoolMatrix<:AbstractMatrix{Bool},
        FloatMatrix<:AbstractMatrix{<:AbstractFloat},
        FloatVector<:AbstractVector{<:AbstractFloat}
}
    wires::Vector{Wire}

    junctions::Dict{Indexes, Point}

    A::BoolMatrix
    G::FloatMatrix
    Y::FloatMatrix
    V::FloatVector

    grounds::Vector{Int64}
end
