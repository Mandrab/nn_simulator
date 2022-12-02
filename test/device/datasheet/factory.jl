using .NNs.Devices.Datasheets

@testset "Datasheet creation from density" begin
    for i in 1:100
        ds = from_density(i, 20, 10, 1234)
        D = ds.wires_count * (10 ^ 2) / (20 ^ 2)

        @test D ≈ i atol=0.05
    end
end
