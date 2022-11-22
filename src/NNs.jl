module NNs

    module Devices

        module Datasheets

            # include the datasheet data
            include("./device/datasheet/datasheet.jl")
            include("./device/datasheet/factory.jl")

        end

        # include the device data
        include("./device/device.jl")
        include("./device/factory.jl")

    end

    module Stimulators

        # include the device stimulator
        include("./stimulator/stimulator.jl")

    end

end
