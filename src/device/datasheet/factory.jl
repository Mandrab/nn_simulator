export from_density

"""
Returns a Datasheet that describes a device with a given density.

# Parameters:
- `density::AbstractFloat`: Desired network density.
- `size: int`: Device package size (micro-meter).
- `wires_length: float`: Length of a single nanowire (micro-meter).
- `seed: int`: Device generation seed.
# Returns:
- `Datasheet`: The datasheet of a device respecting the specified constraints.
"""
function from_density(
        density::AbstractFloat,
        size::Integer,
        wires_length::AbstractFloat,
        seed::Integer
)::Datasheet

    @info "Generating a datasheet with: " density

    # calculate number of wires needed to reach the density
    wires = Int(floor(density * size ^ 2 / wires_length ^ 2))

    return Datasheet(
        wires_count = wires,
        wires_length_mean = wires_length,
        wires_length_variance = wires_length * 0.35,
        Lx = size, Ly = size,
        seed = seed
    )
end
