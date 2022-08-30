cmake_minimum_required(VERSION 3.23)
project(nanowire_network VERSION 3.0.0 LANGUAGES CXX)

# set default C++ version 20 
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# enable testing of the project
enable_testing()

# add sources and tests subdirectories
add_subdirectory (src)
add_subdirectory (test)
