module Updates

include("./kernels.jl")

using CUDA
using .Kernels
using ...Devices
using ...Devices.Datasheets

export update_conductance!

"""
Update weights of the nanowires junctions.
Original model proposed by Enrique Miranda.

# Parameters:
- `device::Device`: The device/network to which update the conductance.
  It will be modified by the function.
- `datasheet::Datasheet`: The device specification.
- `Δt::AbstractFloat`: Time elapsed from the last update.
"""
function update_conductance!(
        device::Device,
        datasheet::Datasheet,
        Δt::AbstractFloat
)
    G = device.G
    Y = device.Y
    A = device.A
    V = device.V
    kp, eta_p = datasheet.kp, datasheet.eta_p
    kd, eta_d = datasheet.kd, datasheet.eta_d
    Y_min, Y_max = datasheet.Y_min, datasheet.Y_max

    # compile the kernel without running it
    kernel = @cuda launch=false kernel!(
        G, Y, A, V, kp, eta_p, kd, eta_d, Y_min, Y_max, Δt
    )

    # calculate the optimal number of threads and blocks
    threads, blocks = optimize(kernel, device.G)

    # run the kernel with the optimized configuration
    kernel(
        # data parameters
        G, Y, A, V, kp, eta_p, kd, eta_d, Y_min, Y_max, Δt;

        # configuration parameters
        threads, blocks
    )
end

"""
Kernel for the conductance update.

# Parameters:
- `G::CuMatrix`: matrix containing the conductance of each junction.
  It will be modified by the function.
- `Y::CuMatrix`: matrix containing the admittance of each junction.
  It will be modified by the function.
- `A::CuMatrix`: adjacency matrix representing the junctions of the wires.
- `V::CuArray`: array containing the wires voltage value.
- `kp::AbstractFloat`: One of the junction potentiation coefficient.
- `eta_p::Int`: One of the junction potentiation coefficient.
- `kd::AbstractFloat`: One of the junction depression coefficient.
- `eta_d::Int`: One of the junction depression coefficient.
- `Y_min::AbstractFloat`: Minimum admittance value.
- `Y_max::AbstractFloat`: Maximum admittance value.
- `Δt::AbstractFloat`: Time elapsed from the last update.
"""
function kernel!(
        G, Y,                                           # I / O
        A, V, kp, eta_p, kd, eta_d, Y_min, Y_max, Δt    # Inputs
)
    i = threadIdx().x + (blockIdx().x - 1) * blockDim().x
    j = threadIdx().y + (blockIdx().y - 1) * blockDim().y

    # control boundary overflow
    width, height = size(G)
    if i > width || j > height
        return
    end

    # if there is no junction connecting the two wires, exit
    @inbounds if ! A[i, j]
        return
    end

    # calculate the delta voltage on each junction
    @inbounds ΔV = abs(V[i] - V[j])

    # compute the potentiation and depression coefficients
    kp *= exp(eta_p * ΔV)
    kd *= exp(-eta_d * ΔV)
    kpd = kp + kd

    # calculate and set the conductance
    partial = kd / kp * G[i, j] * exp(-Δt * kpd)
    @inbounds G[i, j] = kp / kpd * (1 + partial)

    # calculate and set circuit admittance
    @inbounds Y[i, j] = Y_min + G[i, j] * (Y_max - Y_min)

    return
end

end
