export connected_components, largest_connected_component, prune

"""
Finds the connected components from a given adjacency matrix.

# Parameters:
- `matrix::AbstractMatrix{Bool}`: The adjacency matrix representing the network.

# Returns:
- `Dict{Int, Set{Int}}`: A mapping between a connected component index
  and the set of connected nodes.
"""
function connected_components(matrix::AbstractMatrix{Bool})::Dict{Int, Set{Int}}
    unvisited_nodes = Set(1:size(matrix, 1))
    mapping = Dict{Int, Set{Int}}()
    component_count = 0

    # get unvisited neighboors (i.e., the nodes connected to the node)
    function neighboors(node_id::Int)::Vector{Int}
        n = matrix[:, node_id] .* collect(1:size(matrix, 1))
        n = filter(x -> x in unvisited_nodes, n)
        return filter(x -> x != 0, n)
    end

    # visit the node adding it to the mapping and searching its neighboors
    function visit_node(node_id::Int)
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
- `mapping::Dict{Int, Set{Int}}`: The mapping between connected components and the belonging nodes.

# Returns:
- `Vector{Int}`: The set of nodes belonging to the largest connected component.
"""
largest_connected_component(mapping::Dict{Int, Set{Int}})::Vector{Int} =
    sort(collect(argmax(length, values(mapping))))

"""
Remove every row and column not belonging to the set.

# Parameters:
- `array::AbstractMatrix | AbstractVector`: The matrix/vector to prune.
- `mask::AbstractVector`: The set of indexes to keep (integers, bools, ...).

# Returns:
- `AbstractMatrix | AbstractVector`: The pruned matrix/vector.
"""
prune(array::AbstractMatrix, mask::AbstractVector)::AbstractMatrix = array[mask, mask]
prune(array::AbstractVector, mask::AbstractVector)::AbstractVector = array[mask]
