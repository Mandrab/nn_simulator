include("src/NNs.jl")

using PackageCompiler
using Pkg
using .NNs

# activate the current environment (specified by *.toml)
Pkg.activate(".")

@info "Creating SysImage of the library..."

# create the sysimage of the package
create_sysimage(["NNs"]; sysimage_path="nns.so", precompile_execution_file="src/.precompile.jl")

@info "SysImage ready. Use it with `julia -q [--trace-compile=stderr] --sysimage=nns.so`"
