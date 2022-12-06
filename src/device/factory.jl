include("./util/generators.jl")
include("./util/networks.jl")

using CUDA
using .Devices.Datasheets
using .Devices.Networks

export realize, simplify

"""
Produces the nanowire network device according to its datasheet description.

# Parameters:
- `datasheet::Datasheet`: Datasheet describing the device.

# Returns:
- `Device`: The realized device.
"""
function realize(datasheet::Datasheet)::Device

    @info "Generating a device/network with: " datasheet.wires_count

    # generate the network wires distribution
    wires = drop_wires(datasheet)

    # get junctions list and their positions
    junctions = detect_junctions(wires)

    # generate graph object and adjacency matrix
    A = CuArray(calculate_adjacency(junctions, datasheet))

    # calculate remaining data
    G = CUDA.zeros(size(A))
    Y = datasheet.Y_min .* A
    V = CUDA.zeros(datasheet.wires_count)

    return Device(wires, junctions, A, G, Y, V, 0)
end

"""
Simplifies the device removing everything except the largest connected component.

# Parameters:
- `device::Device`: The device to simplify.
- `ds::Datasheet`: Datasheet describing the passed device.

# Returns:
- `Tuple{Device, Datasheet}`: The simplified device and the updated datasheet
  (i.e., withouth the removed wires and junctions).
"""
function simplify(device::Device, ds::Datasheet)::Tuple{Device, Datasheet}

    @info "Simplify the device keeping only the largest connected component"

    # find the connected components in the network
    mapping = connected_components(Array(device.A))

    # get the index of the nodes belonging to the largest connected component
    mask = largest_connected_component(mapping)

    # create a lookup table to map the old wires index to a new one
    lut = Dict(map(ab -> ab[2] => ab[1], enumerate(mask)))

    # remove the nodes not belonging to the largest connected component
    wires = device.wires[mask]

    # remove the junctions between nodes not in the connected component
    # and update the wires index
    junctions = Dict(
        (lut[i] => lut[j]) => p
        for ((i, j), p) in collect(device.junctions)
        if i ∈ mask
    )

    # delete all the components except the largest one
    A = prune(device.A, mask)
    G = prune(device.G, mask)
    Y = prune(device.Y, mask)
    V = prune(device.V, mask)

    # create the new structures
    device = Device(wires, junctions, A, G, Y, V, 0)
    datasheet = Datasheet(
        length(wires), ds.wires_length_mean, ds.wires_length_variance,
        ds.size, ds.kp, ds.eta_p, ds.kd, ds.eta_d, ds.Y_min, ds.Y_max, ds.seed
    )
    return device, datasheet
end
