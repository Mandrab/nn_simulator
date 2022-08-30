# create a library from the source files
add_library(
    nanowire_network
    STATIC
        nanowire_network.h
        model/device/datasheet/datasheet.h
        model/device/datasheet/factory.cpp
        model/device/datasheet/factory.h
        model/device/datasheet/serialization.cpp
        model/device/datasheet/serialization.h
)

# make the src directory content public
target_include_directories(
    nanowire_network
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}
)
