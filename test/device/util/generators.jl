using .NNs.Devices
using .NNs.Devices.Datasheets

include("../../../src/device/device.jl")
include("../../../src/device/util/generators.jl")

@testset "Wires dropcast consistency" begin
    ds = from_density(5.0, 100)
    ws = drop_wires(ds)

    @test length(ws) == ds.wires_count

    for w in ws
        c, s, e, l = w
        @test s[1] < c[1] < e[1] || s[1] > c[1] > e[1]
        @test s[2] < c[2] < e[2] || s[2] > c[2] > e[2]
        @test sqrt((s[1] - e[1])^2 + (s[2] - e[2])^2) ≈ l atol=1e-10
        @test sqrt((s[1] - c[1])^2 + (s[2] - c[2])^2) ≈ l / 2 atol=1e-10
        @test sqrt((e[1] - c[1])^2 + (e[2] - c[2])^2) ≈ l / 2 atol=1e-10
    end
end

@testset "Junctions detection constistency" begin
    ds = from_density(5.0, 100)
    ws = drop_wires(ds)
    js = detect_junctions(ws, ds)

    for j in js
        indexes, point = j
        x, y = point

        # test that the junction belong to the segment of both wires
        for index in indexes
            _, s, e, _ = ws[index]
            sx, sy = s
            ex, ey = e

            @test (y - sy) * (ex - sx) - (x - sx) * (ey - sy) ≈ 0 atol=1e-10
        end
    end
end
