include("NNs.jl")

using .NNs.Devices
using .NNs.Devices.Datasheets
using .NNs.Stimulators

precompile(from_density, (Float64, Int64, Float64, Int64))
precompile(realize, (Datasheet, ))
precompile(simplify, (Device, Datasheet))
precompile(stimulate!, (Device, Datasheet, Float64, Vector{Float64}))
