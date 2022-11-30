module Kernels

using CUDA

export optimize

"""
Calculate the optimal number of threads and blocks to run the kernel.

# Parameters:
- `kernel::Function`: The compiled kernel function (use `@cuda launch=false`).
- `array::CuArray`: The largest 1D or 2D array used by the kernel function.

# Returns:
- `Tuple{Integer, Integer}`: If the array is 1D.
  The first value is the number of threads, the second the number of blocks.
- `Tuple{Tuple{Integer, Integer}, Tuple{Integer, Integer}}`: If the array is 2D.
  The first value is the number of 2D threads, the second the number of 2D blocks.
"""
function optimize(kernel::CUDA.HostKernel, array::CuArray)

    # extract configuration via occupancy API
    config = launch_configuration(kernel.fun)

    # number of threads should not exceed array size. Additionally,
    # we cannot have more thread than the ones supported by a block
    threads = min(length(array), config.threads)

    # smallest integer larger than or equal to length(A) / threads
    blocks = cld(length(array), threads)

    # return the optimal configuration to launch the kernel
    if array isa CuMatrix
        threads = Int(floor(sqrt(threads)))
        return (threads, threads), (blocks, blocks)
    else
        return threads, blocks
    end
end

end
