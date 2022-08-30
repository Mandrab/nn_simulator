/**
 * @file serialization.h
 * @author Paolo Baldini (paolo.baldini7@unibo.it)
 * @brief Collection of functions for Datasheet (de-)serialization.
 * @version 0.1
 * @date 2022-08-30
 * 
 * @copyright Copyright (c) 2022
 */
#ifndef __DATASHEET_SERIALIZATION__
#define __DATASHEET_SERIALIZATION__

#include "datasheet.h"

namespace model::device::datasheet {

    /**
     * @brief  Serialize a Datasheet type into a float array
     * @param  datasheet: The datasheet to serialize
     * @retval An array containing the serialized data
     */
    float* serialize(const Datasheet* datasheet);

    /**
     * @brief  De-serialize floats into a Datasheet type
     * @param  data: The serialized data
     * @retval The returned datasheet
     */
    Datasheet* deserialize(const float *data);

}

#endif
