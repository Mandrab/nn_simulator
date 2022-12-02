using Distributions: Normal
using Lazy
using Random
using .Devices.Datasheets

"""
Drop wires in the package according to the datasheet description.

# Parameters:
- `datasheet::Datasheet`: Datasheet describing the device.

# Returns:
- `Vector{Wire}`: A sequence of dropped wires, including their centroid,
  start and end position, and lenght.
"""
function drop_wires(datasheet::Datasheet)::Vector{Wire}

    @debug "Dropping wires"

    # set the random seed for the device generation
    Random.seed!(datasheet.seed)

    # generate the (positive) lengths of the wires
    distribution = Normal(datasheet.wires_length_mean, datasheet.wires_length_variance)
    generator = map(x -> rand(distribution), Lazy.range())
    generator = filter(x -> x > 0, generator)
    wires_length = collect(take(datasheet.wires_count, generator))

    # generate the centroids of the wires
    xc = rand(datasheet.wires_count) * datasheet.size
    yc = rand(datasheet.wires_count) * datasheet.size
    theta = rand(datasheet.wires_count) * pi

    # generate the coordinates for one wire end
    xa = xc - wires_length / 2.0 .* map(cos, theta)
    ya = yc - wires_length / 2.0 .* map(sin, theta)

    # generate the coordinates for the other wire end
    xb = xc + wires_length / 2.0 .* map(cos, theta)
    yb = yc + wires_length / 2.0 .* map(sin, theta)

    # create sets representing centroid, start and end points
    centroids = map((x, y) -> x => y, xc, yc)
    starts = map((x, y) -> x => y, xa, ya)
    finish = map((x, y) -> x => y, xb, yb)

    # create and return the set of wires of the network
    return collect(zip(centroids, starts, finish, wires_length))
end

"""
Detect the wires junctions.

# Parameters:
- `wires::Vector{Wire}`: The set of dropped wires.

# Returns:
- `Dict{Indexes, Point}`: A mapping between wires and junction position.
"""
function detect_junctions(wires::Vector{Wire})::Dict{Indexes, Point}

    @debug "Detecting junctions"

    # calculate distance between start and end point
    delta_x = [sx - ex for (_, (sx, _), (ex, _), _) in wires]
    delta_y = [sy - ey for (_, (_, sy), (_, ey), _) in wires]
    x_left = [min(sx, ex) for (_, (sx, _), (ex, _), _) in wires]
    x_right = [max(sx, ex) for (_, (sx, _), (ex, _), _) in wires]
    y_bottom = [min(sy, ey) for (_, (_, sy), (_, ey), _) in wires]
    y_up = [max(sy, ey) for (_, (_, sy), (_, ey), _) in wires]
    m = [sx * ey - sy * ex for (_, (sx, sy), (ex, ey), _) in wires]

    junctions = Dict{Indexes, Point}()
    for i in 1:length(wires)
        for j in (i+1):length(wires)
            c = delta_x[i] * delta_y[j] - delta_y[i] * delta_x[j]

            # if there is no intersection check the next one
            if abs(c) < 0.01
                continue
            end

            a, b = m[i], m[j]

            x = (a * delta_x[j] - b * delta_x[i]) / c
            y = (a * delta_y[j] - b * delta_y[i]) / c

            # exclude junction points out of the points area
            if (
                x_left[i] <= x <= x_right[i] &&
                x_left[j] <= x <= x_right[j] &&
                y_bottom[i] <= y <= y_up[i] &&
                y_bottom[j] <= y <= y_up[j]
            )
                junctions[i => j] = x => y
            end
        end
    end

    return junctions
end

"""
Generate the adjacency matrix from the junctions mapping.

# Parameters:
- `junctions::Dict{Indexes, Point}`: The junctions mapping.
- `datasheet::Datasheet`: The datasheet describing the device.

# Returns:
- `Matrix{Bool}`: The generated adjacency matrix.
"""
function calculate_adjacency(junctions::Dict{Indexes, Point}, datasheet::Datasheet)::Matrix{Bool}

    @debug "Calculating adjacency"

    matrix = falses(datasheet.wires_count, datasheet.wires_count)
    for ((x, y), _) in junctions
        matrix[x, y] = matrix[y, x] = true
    end

    return matrix
end
