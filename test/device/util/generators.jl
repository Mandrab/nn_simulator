using .NNs.Devices: drop_wires, detect_junctions, calculate_adjacency
using .NNs.Devices.Datasheets

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

@testset "Junctions detection consistency" begin
    ds = from_density(5.0, 100)
    ws = drop_wires(ds)
    js = detect_junctions(ws)

    # test that a junction position belongs to the segment of both wires
    for (indexes, (x, y)) in js
        for index in indexes
            _, s, e, _ = ws[index]
            sx, sy = s
            ex, ey = e

            @test (y - sy) * (ex - sx) - (x - sx) * (ey - sy) ≈ 0 atol=1e-10
        end
    end
end

@testset "Adjacency calculation consistency" begin
    ds = from_density(5.0, 100)
    ws = drop_wires(ds)
    js = detect_junctions(ws)
    adj = calculate_adjacency(js, ds)

    @test size(adj) == (ds.wires_count, ds.wires_count)

    # test that each junction appears in the adjacency matrix
    for i in 1:ds.wires_count
        for j in 1:ds.wires_count

            if (i => j) in keys(js) || (j => i) in keys(js)
                @test adj[i, j] && adj[j, i]
            else
                @test ! adj[i, j] && ! adj[j, i]
            end
        end
    end
end
