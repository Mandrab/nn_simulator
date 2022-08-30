#include <gtest/gtest.h>

#include "nanowire_network.h"

using namespace model::device::datasheet;

const Datasheet DEFAULT;

TEST(Serialization, StructToData) {

    // serialize the data through the function
    float* data = serialize(&DEFAULT);

    // set the expected data array
    int data_length = 13;
    float expected_data[data_length] = {
        (float)DEFAULT.wires_count,
        (float)DEFAULT.centroid_dispersion,
        DEFAULT.mean_length,
        DEFAULT.std_length,
        (float)DEFAULT.Lx,
        (float)DEFAULT.Ly,
        DEFAULT.kp0,
        (float)DEFAULT.eta_p,
        DEFAULT.kd0,
        (float)DEFAULT.eta_d,
        DEFAULT.Y_min,
        DEFAULT.Y_max,
        (float)DEFAULT.seed
    };

    // get array length
    int expected_data_length = sizeof(expected_data) / sizeof(expected_data[0]);
    
    // check the equality
    EXPECT_EQ(data_length, expected_data_length);
    for (int i = 0; i < data_length; i++)
        EXPECT_EQ(data[i], expected_data[i]);

    delete data;
}

TEST(Serialization, DataToStruct) {

    // set the data array
    float expected_data[13] = {
        (float)DEFAULT.wires_count,
        (float)DEFAULT.centroid_dispersion,
        DEFAULT.mean_length,
        DEFAULT.std_length,
        (float)DEFAULT.Lx,
        (float)DEFAULT.Ly,
        DEFAULT.kp0,
        (float)DEFAULT.eta_p,
        DEFAULT.kd0,
        (float)DEFAULT.eta_d,
        DEFAULT.Y_min,
        DEFAULT.Y_max,
        (float)DEFAULT.seed
    };

    // deserialize the data through the function
    Datasheet* data = deserialize(expected_data);

    // check the equality
    EXPECT_EQ(data->wires_count, expected_data[0]);
    EXPECT_EQ(data->centroid_dispersion, expected_data[1]);
    EXPECT_EQ(data->mean_length, expected_data[2]);
    EXPECT_EQ(data->std_length, expected_data[3]);
    EXPECT_EQ(data->Lx, expected_data[4]);
    EXPECT_EQ(data->Ly, expected_data[5]);
    EXPECT_EQ(data->kp0, expected_data[6]);
    EXPECT_EQ(data->eta_p, expected_data[7]);
    EXPECT_EQ(data->kd0, expected_data[8]);
    EXPECT_EQ(data->eta_d, expected_data[9]);
    EXPECT_EQ(data->Y_min, expected_data[10]);
    EXPECT_EQ(data->Y_max, expected_data[11]);
    EXPECT_EQ(data->seed, expected_data[12]);

    delete data;
}
