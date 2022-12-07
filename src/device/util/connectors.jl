"""
Add a ground to the device.
This adds a row and a column at the bottom & right of the matrixes.
Additionally, it adds the ground index to the grounds list.

# Parameters:
- `device::Device`: The device to which add the ground.
"""
function ground!(device::Device)

    # get the number of element in the device
    count = size(device.A, 1)

    """Pad the matrix with zeros at the bottom and right."""
    pad(M) = [[M; zeros(1, count)] zeros(count + 1)]

    # update the arrays of the device
    device.A = pad(device.A)
    device.G = pad(device.G)
    device.Y = pad(device.Y)
    device.V = [device.V; 0]

    # append the ground index in the list
    append!(device.grounds, count + 1)
end

"""
Ground the selected wire of the device network.

# Parameters:
- `device::Device`: The device to which the wire belongs to.
- `wire_index::Integer`: The index of the wire to ground.
"""
ground!(device::Device, wire_index::Integer) = append!(device.grounds, wire_index)

"""
Connect a grounded resistence to a device wire.

```
°---°
 \ /---------R---------GND
  °
Device    Resistor    Ground
```

# Parameters:
- `device::Device`: The device to which connect the resistance.
- `wire_index::Integer`: The index of the wire to which connect the resistor.
- `resistance::AbstractFloat`: The resistor resistance.

# Returns:
- `Integer`: The index of the ground to which the resistance is connected.
"""
function connect!(
        device::Device,
        wire_index::Integer,
        resistance::AbstractFloat
)::Integer

    # if there is no ground, add it to the device
    if isempty(device.grounds)
        ground!(device)
    end

    # get the index of a ground of the device
    ground_index = first(device.grounds)

    # set a connection in the Adjacency matrix
    device.A[wire_index, ground_index] = true
    device.A[ground_index, wire_index] = true

    # set the junction conductance and admittance TODO
    device.G[wire_index, ground_index] = 0
    device.G[ground_index, wire_index] = 0
    device.Y[wire_index, ground_index] = 1 / resistance
    device.Y[ground_index, wire_index] = 1 / resistance

    return ground_index
end
