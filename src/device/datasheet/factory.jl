export from_density

"""
Returns a Datasheet that describes a device with a given density.

# Parameters:
- `density::Real`: Desired network density.
- `size: Real`: Device package size (micro-meter).
- `wires_length: Real`: Length of a single nanowire (micro-meter).
- `seed: Int`: Device generation seed.

# Returns:
- `Datasheet`: The datasheet of a device respecting the specified constraints.
"""
function from_density(
        density::Real,
        size::Real,
        wires_length::Real,
        seed::Int
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
