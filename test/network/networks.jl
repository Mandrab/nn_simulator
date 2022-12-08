using .NNs.Devices.Networks

@testset "Connected components search" begin
    M = [
        0 1
        1 0
    ] .== 1
    d = connected_components(M)

    @test length(d) == 1
    @test d[1] == Set([1, 2])

    M = [
        0 1 0
        1 0 0
        0 0 0
    ] .== 1
    d = connected_components(M)

    @test length(d) == 2
    @test d[1] == Set([1, 2])
    @test d[2] == Set([3])

    M = [
        0 0 1 0 0 1
        0 0 0 0 1 0
        1 0 0 0 0 1
        0 0 0 0 0 0
        0 1 0 0 0 0
        1 0 1 0 0 0
    ] .== 1
    d = connected_components(M)

    @test length(d) == 3
    @test d[1] == Set([2, 5])
    @test d[2] == Set([4])
    @test d[3] == Set([1, 3, 6])
end

@testset "Largest connected component individuation" begin
    M = [
        0 1
        1 0
    ] .== 1
    d = connected_components(M)
    l = largest_connected_component(d)

    @test l == [1, 2]

    M = [
        0 0 1 0 0 1
        0 0 0 0 1 0
        1 0 0 0 0 1
        0 0 0 0 0 0
        0 1 0 0 0 0
        1 0 1 0 0 0
    ] .== 1
    d = connected_components(M)
    l = largest_connected_component(d)

    @test l == [1, 3, 6]

    M = [
        0 1 0 0 0
        1 0 0 0 0
        0 0 0 0 0
        0 0 0 0 1
        0 0 0 1 0
    ] .== 1
    d = connected_components(M)
    l = largest_connected_component(d)

    @test l == [1, 2] || l == [4, 5]
end

@testset "Vector pruning" begin
    A = [1, 2, 3, 4, 5]

    @test prune(A, []) == []

    A = [1, 2, 3, 4, 5]

    @test prune(A, [1, 3]) == [1, 3]

    A = [1, 2, 3, 4, 5]

    @test prune(A, [1, 2, 3, 4, 5]) == A
end

@testset "Network pruning" begin
    M = [
        0 1
        1 0
    ] .== 1

    @test isempty(prune(M, []))

    M = [
        0 0 1 0 0 1
        0 0 0 0 1 0
        1 0 0 0 0 1
        0 0 0 0 0 0
        0 1 0 0 0 0
        1 0 1 0 0 0
    ] .== 1
    expected = [
        0 0 1
        0 0 0
        1 0 0
    ]
    
    @test prune(M, [2, 4, 5]) == expected

    M = [
        0 1 0 0 0
        1 0 0 0 0
        0 0 0 0 0
        0 0 0 0 1
        0 0 0 1 0
    ] .== 1

    @test prune(M, [1, 2, 3, 4, 5]) == M
end
