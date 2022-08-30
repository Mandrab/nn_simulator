/**
 * @file datasheet.h
 * @author Paolo Baldini (paolo.baldini7@unibo.it)
 * @brief Contains the device properties definition.
 * @version 0.1
 * @date 2022-08-30
 * 
 * @copyright Copyright (c) 2022
 */
#ifndef __DATASHEET__
#define __DATASHEET__

namespace model::device::datasheet {

    #define DEFAULT_SEED 40

    /**
     * @brief Define the static properties of the device
     */
    typedef struct {
        
        int wires_count = 1500;                     ///< Total number of wires to be sampled
        int centroid_dispersion = 200;              ///< Scale parameter for the general normal distribution from which centroids of wires are drawn in mum
        float mean_length = 40.0;                   ///< Average wire length in mum
        float std_length = 14.0;                    ///< Length of the nano-wire in mum (default = 14)

        // device size
        int Lx = 500;                               ///< Horizontal length of the device in mum
        int Ly = 500;                               ///< Vertical length of the device in mum

        // update_edge_weights parameters
        float kp0 = 0.0001;
        int eta_p = 10;
        float kd0 = 0.5;
        int eta_d = 1;

        // admittance
        float Y_min = 0.001;
        float Y_max = 0.001 * 100;

        int seed = DEFAULT_SEED;                    ///< Seed of the random number generator to always generate the same distribution

    } Datasheet;

}

#endif
