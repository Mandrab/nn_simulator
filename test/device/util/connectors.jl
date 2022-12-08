using .NNs.Devices
using .NNs.Devices.Datasheets
using .NNs.Devices.Utils

@testset "Device grounding" begin
    ds = from_density(5.0)
    dv = realize(ds)

    A = copy(dv.A)
    G = copy(dv.G)
    Y = copy(dv.Y)
    V = copy(dv.V)

    """Check that B is A padded with zeroes."""
    ispadded(A, B, s = 1) = A == B[1:end - s, 1:end - s] &&
        all(B[end, :] .== 0) && all(B[:, end] .== 0)

    ground!(dv)

    # check that an additional row and column has been added
    @test size(dv.A) == (ds.wires_count + 1, ds.wires_count + 1)
    @test dv.grounds == [ds.wires_count + 1]

    @test ispadded(A, dv.A)
    @test ispadded(G, dv.G)
    @test ispadded(Y, dv.Y)
    @test V == dv.V[1:end - 1] && V[end] == 0

    ground!(dv)

    # check that an additional row and column has been added
    @test size(dv.A) == (ds.wires_count + 2, ds.wires_count + 2)
    @test dv.grounds == [ds.wires_count + 1, ds.wires_count + 2]

    @test ispadded(A, dv.A, 2)
    @test ispadded(G, dv.G, 2)
    @test ispadded(Y, dv.Y, 2)
    @test V == dv.V[1:end - 2] && V[end] == 0
end

@testset "Wire grounding" begin
    ds = from_density(5.0)
    dv = realize(ds)

    ground!(dv, 2)

    @test dv.grounds == [2]

    ground!(dv, 5)

    @test dv.grounds == [2, 5]
end

@testset "Load connection" begin
    ds = from_density(5.0)
    dv = realize(ds)

    A = copy(dv.A)
    G = copy(dv.G)
    Y = copy(dv.Y)
    V = copy(dv.V)

    connect!(dv, 2, 12345.0)

    # connecting without any ground set should trigger a ground addition
    @test dv.grounds == [ds.wires_count + 1]
    @test size(dv.A) == (ds.wires_count + 1, ds.wires_count + 1)
    @test size(dv.G) == (ds.wires_count + 1, ds.wires_count + 1)
    @test size(dv.Y) == (ds.wires_count + 1, ds.wires_count + 1)
    @test length(dv.V) == ds.wires_count + 1

    # the wire two should now be connected with the ground
    @test dv.A[2, end] == dv.A[end, 2] == true
    @test dv.G[2, end] == dv.G[end, 2] == 0
    @test dv.Y[2, end] ≈ 1 / 12345.0 atol=1e-10
    @test dv.Y[end, 2] ≈ 1 / 12345.0 atol=1e-10

    connect!(dv, 3, 54321.0)

    # connecting with a ground shouldn't trigger a ground addition
    @test dv.grounds == [ds.wires_count + 1]
    @test size(dv.A) == (ds.wires_count + 1, ds.wires_count + 1)
    @test size(dv.G) == (ds.wires_count + 1, ds.wires_count + 1)
    @test size(dv.Y) == (ds.wires_count + 1, ds.wires_count + 1)
    @test length(dv.V) == ds.wires_count + 1

    # the wire two should now be connected with the ground
    @test dv.A[3, end] == dv.A[end, 3] == true
    @test dv.G[3, end] == dv.G[end, 3] == 0
    @test dv.Y[3, end] ≈ 1 / 54321.0 atol=1e-10
    @test dv.Y[end, 3] ≈ 1 / 54321.0 atol=1e-10

end
