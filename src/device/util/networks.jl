module Networks

using CUDA

export connected_components, largest_connected_component, prune

"""
Finds the connected components from a given adjacency matrix.

# Parameters:
- `matrix::Matrix{Bool}`: The adjacency matrix representing the network.
# Returns:
- `Dict{Int64, Set{Int64}}`: A mapping between a connected component index
  and the set of connected nodes.
"""
function connected_components(matrix::Matrix{Bool})::Dict{Int64, Set{Int64}}
    unvisited_nodes::Set{Int64} = Set(1:size(matrix, 1))
    mapping = Dict{Int64, Set{Int64}}()
    component_count = 0

    # get unvisited neighboors (i.e., the nodes connected to the node)
    function neighboors(node_id::Int64)::Vector{Int64}
        n = matrix[:, node_id] .* collect(1:size(matrix, 1))
        n = filter(x -> x in unvisited_nodes, n)
        return filter(x -> x != 0, n)
    end

    # visit the node adding it to the mapping and searching its neighboors
    function visit_node(node_id::Int64)
        push!(mapping[component_count], node_id)
        delete!(unvisited_nodes, node_id)
        foreach(visit_node, neighboors(node_id))
    end

    # check all the nodes of the network
    while !isempty(unvisited_nodes)

        # get the component origin and remove it from the list of unvisited nodes
        origin = pop!(unvisited_nodes)

        # save the origin in a new mapping
        mapping[component_count += 1] = Set(origin)

        # check every node connected with the origin
        foreach(visit_node, neighboors(origin))
    end

    return mapping
end

"""
Find the largest connected component in a given mapping.

# Parameters:
- `mapping::Dict{Int64, Set{Int64}}`: The mapping between connected components and the belonging nodes.
# Returns:
- `Vector{Int64}`: The set of nodes belonging to the largest connected component.
"""
largest_connected_component(mapping::Dict{Int64, Set{Int64}})::Vector{Int64} =
    sort(collect(argmax(length, values(mapping))))

"""
Remove every row and column not belonging to the set.

# Parameters:
- `matrix::CuArray`: The matrix/array to prune.
- `mask::Vector`: The set of index to keep.
# Returns:
- `CuArray`: The pruned matrix/array.
"""
prune(matrix::CuArray, mask::Vector)::CuArray =
    matrix isa CuMatrix ? matrix[mask, mask] : matrix[mask]

end
