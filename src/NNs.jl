module NNs

    """Utilities to work with networks in their matrix representation."""
    module Networks

        include("./network/networks.jl")
    end

    """Definition and utilities for nanowire-network devices."""
    module Devices

        """Definition and utilities for the formal representation of devices."""
        module Datasheets

            include("./device/datasheet/datasheet.jl")
            include("./device/datasheet/factory.jl")
        end

        include("./device/device.jl")
        include("./device/factory.jl")

        """Utilities for the device manipulation and optimization."""
        module Utils

            include("./device/util/connectors.jl")
            include("./device/util/optimizations.jl")
        end

    end

    """Utilities for the device stimulation."""
    module Stimulators

        include("./stimulator/stimulator.jl")
    end

end
