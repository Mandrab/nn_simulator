/**
 * @file main.cpp
 * @author Paolo Baldini (paolo.baldini7@unibo.it)
 * @brief Runs all the included project tests.
 * @version 0.1
 * @date 2022-08-30
 * 
 * @copyright Copyright (c) 2022
 */
#include <gtest/gtest.h>

#include "model/device/datasheet/serialization-test.cpp"

int main(int argc, char **argv)
{
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
