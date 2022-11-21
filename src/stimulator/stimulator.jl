include("./mna.jl")
include("./update.jl")

using .MNAs
using .Updates
using ..Devices
using ..Devices.Datasheets

export stimulate!

"""
Stimulate the network through voltage-inputs on specific wires.
The function modifies the device state.

# Parameters:
- `device::Device`: The device to stimulate. It will be modified by the function.
- `datasheet::Datasheet`: The device technical description.
- `Δt::AbstractFloat`: Time elapsed from the last update.
- `inputs::Vector{Float64}`: The voltage values of the network wires.
  If the value is 0, the wire is not an input / fixed voltage node, and vice-versa.
"""
function stimulate!(
        device::Device,
        datasheet::Datasheet,
        Δt::AbstractFloat,
        inputs::Vector{Float64}
)

    # update the junctions conductance according to the voltage distribution
    update_conductance!(device, datasheet, Δt)

    # update the voltage distribution after the stimulation
    modified_voltage_node_analysis!(device, inputs)
end
