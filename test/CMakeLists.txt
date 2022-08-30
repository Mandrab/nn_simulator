# download the GoogleTest suite
include(FetchContent)
FetchContent_Declare(
    googletest
    GIT_REPOSITORY https://github.com/google/googletest.git
    GIT_TAG release-1.12.1
)
FetchContent_MakeAvailable(googletest)

# create an executable test
add_executable(nanowire_network-test main.cpp)

# link the library and GTest with the test code
target_link_libraries(
    nanowire_network-test
    PRIVATE
        gtest_main
        nanowire_network
)

# add a test that run the generated executable
add_test(NAME nanowire_network-test COMMAND nanowire_network-test)
