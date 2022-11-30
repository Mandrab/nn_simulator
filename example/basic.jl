using .NNs.Devices
using .NNs.Devices.Datasheets
using .NNs.Stimulators

function main(density::AbstractFloat, size::Int, iterations::Int)

    # generate random seed
    seed = rand(1:9999)

    # generate device
    datasheet = from_density(density, size, 15.0, seed)
    device = realize(datasheet)
    device, datasheet = simplify(device, datasheet)

    # create stimulus
    voltages = collect(map(v ->
        Float64(v >= datasheet.wires_count -1 ? v : 0),
        1:datasheet.wires_count
    ))

    # stimulate
    for _ in 1:iterations
        stimulate!(device, datasheet, 0.1, voltages)
    end

end

@time main(5.0, 100, 200)
@time main(5.0, 150, 200)
