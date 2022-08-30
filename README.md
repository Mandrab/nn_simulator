**Nanowire Network Simulator - Library**

Simulator of the self-organized *nanowire network* developed in Torino.
The code was originally written by Gianluca Milano, Enrique Miranda and Carlo Ricciardi (DOI: https://doi.org/10.1016/j.neunet.2022.02.022), and then here modified to be used as a library.
The original code can be found at the following link: https://github.com/MilanoGianluca/Memristive_Nanowire_Networks_Connectome

The module *wires* used to create the network structure was imported and adapted from the model reported in the work by Loeffler, Alon, et al.,"Topological properties of neuromorphic nanowire networks", Frontiers in Neuroscience 14 (2020): 184. https://github.com/aloe8475/CODE/blob/master/Analysis/Generate%20Networks/wires.py

--------------------------------------------------------------------------------

The code allows performing analysis of the structural and functional connectivity of the memristive NW network.

Run the code tests with:
'''
clear; cmake -S . -B build; cmake --build build; cd build && ctest; cd ..
'''