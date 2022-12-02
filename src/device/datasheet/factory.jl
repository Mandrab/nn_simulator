export from_density

"""
Returns a Datasheet that describes a device with the required characteristics.

# Parameters:
- `density::Real`: Desired network density.
- `size: Real`: Device package size in µm (micro-meters).
- `wires_length: Real`: Length of a single nanowire in µm (micro-meters).
- `seed: Int`: Device generation seed.

# Returns:
- `Datasheet`: The datasheet of a device respecting the specified constraints.
"""
function from_density(
        density::Real,
        size::Real = 500,
        wires_length::Real = 14.0,
        seed::Int = 1234
)::Datasheet

    @info "Generating a datasheet with: " density

    # calculate number of wires needed to reach the density
    wires = Int(floor(density * size ^ 2 / wires_length ^ 2))

    return Datasheet(
        wires_count = wires,
        wires_length_mean = wires_length,
        wires_length_variance = wires_length * 0.35,
        size = size,
        seed = seed
    )
end
