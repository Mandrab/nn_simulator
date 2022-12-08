using AMDGPU
using CUDA

export optimize

"""
This method masks all the logic in the possible choice of GPU accelleration.
The supported GPU programming types are CUDA and AMD.

# Parameters:
- `array::AbstractArray{<:Real}`: The array to move to the most efficient device.

# Returns
- `Array{<:Real}`: The array moved to the most efficient device.
"""
function optimizze(array::T) where T<:AbstractArray{<:Real}

    # if CUDA is supported return a CuArray
    if CUDA.functional()
        return CuArray(array)
    end

    # if AMD GPU is supported return a ROCArray
    # TODO to be tested
    if AMDGPU.functional()
        return ROCArray(array)
    end

    # the most efficient device is the host
    return array
end

"""
Optimize the nanowire-network device for its simulation.
This possibly consists in moving the matrixes to a GPU device.

# Parameters:
- `device::Device`: The nanowire-network device to optimize.

# Returns:
- `Device`: The optimized device.
"""
optimize(device::Device) = Device(
    device.wires,
    device.junctions,
    optimizze(device.A),
    optimizze(device.G),
    optimizze(device.Y),
    optimizze(device.V),
    device.grounds
)
