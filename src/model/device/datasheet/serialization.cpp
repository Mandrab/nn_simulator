/**
 * @file serialization.cpp
 * @author Paolo Baldini (paolo.baldini7@unibo.it)
 * @brief Implementation of the serialization.h functions.
 * @version 0.1
 * @date 2022-08-31
 * 
 * @copyright Copyright (c) 2022
 */
#include "serialization.h"

namespace model::device::datasheet {

    float* serialize(const Datasheet* datasheet)
    {
        float* data = new float[13];
        int index = 0;

        data[index++] = datasheet->wires_count;
        data[index++] = datasheet->centroid_dispersion;
        data[index++] = datasheet->mean_length;
        data[index++] = datasheet->std_length;
        data[index++] = datasheet->Lx;
        data[index++] = datasheet->Ly;
        data[index++] = datasheet->kp0;
        data[index++] = datasheet->eta_p;
        data[index++] = datasheet->kd0;
        data[index++] = datasheet->eta_d;
        data[index++] = datasheet->Y_min;
        data[index++] = datasheet->Y_max;
        data[index] = datasheet->seed;

        return data;
    }

    Datasheet* deserialize(const float *data)
    {
        Datasheet* datasheet = new Datasheet;
        int index = 0;

        datasheet->wires_count = data[index++];
        datasheet->centroid_dispersion = data[index++];
        datasheet->mean_length = data[index++];
        datasheet->std_length = data[index++];
        datasheet->Lx = data[index++];
        datasheet->Ly = data[index++];
        datasheet->kp0 = data[index++];
        datasheet->eta_p = data[index++];
        datasheet->kd0 = data[index++];
        datasheet->eta_d = data[index++];
        datasheet->Y_min = data[index++];
        datasheet->Y_max = data[index++];
        datasheet->seed = data[index];

        return datasheet;
    }

}
