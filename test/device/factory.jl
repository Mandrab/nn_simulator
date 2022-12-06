using CUDA
using .NNs.Devices.Datasheets
using .NNs.Devices

CUDA.allowscalar() do

function correct_device(dv, ds)

    # test the amount of wires
    @test length(dv.wires) == ds.wires_count
    @test size(dv.A) == (ds.wires_count, ds.wires_count)
    @test size(dv.G) == (ds.wires_count, ds.wires_count)
    @test size(dv.Y) == (ds.wires_count, ds.wires_count)
    @test size(dv.V) == (ds.wires_count, )

    # test the junction presence
    for ((x, y), _) in dv.junctions
        @test x <= ds.wires_count
        @test y <= ds.wires_count
    end

    # test the junction presence and consistency in the matrixes
    kys = keys(dv.junctions)
    for i in 1:ds.wires_count
        for j in i:ds.wires_count

            if (i => j) in kys || (j => i) in kys
                @test dv.A[i, j] == dv.A[j, i] == true
                @test dv.Y[i, j] == dv.Y[j, i] == ds.Y_min
            else
                @test dv.A[i, j] == dv.A[j, i] == false
                @test dv.Y[i, j] == dv.Y[j, i] == 0
            end

            @test dv.G[i, j] == dv.G[j, i] == 0
        end

        @test dv.V[i] == 0
    end
end

@testset "Network realization" begin
    ds = Datasheet(wires_count=250)
    dv = realize(ds)

    correct_device(dv, ds)
end

@testset "Network simplification" begin
    ds = Datasheet(wires_count=250)
    dv = realize(ds)
    dvs, dss = simplify(dv, ds)

    correct_device(dvs, dss)
end

end
