# Nanowire Network simulator (NNs) — library

Simulator of a self-organized network composed of silver-nanowires.
It allows to perform the analysis of the structural and functional connectivity of the memristive NW network.
The physical device that this library simulates has been built @ Polytechnic of Turin by _Gianluca Milano_, _Enrique Miranda_ and _Carlo Ricciardi_ (DOI: https://doi.org/10.1016/j.neunet.2022.02.022).
They also developed a [pioneering version](https://github.com/MilanoGianluca/Memristive_Nanowire_Networks_Connectome) of the simulator, that has been later rewritten by _Paolo Baldini_ to be used as a library in his [master thesis](https://amslaurea.unibo.it/25396/).
The result is a much faster simulator, able to take advantage of the GPU computational capabilities.
The support is currently limited to NVidia GPUs (through CUDA), but will be extended to alternative brands.

The module *wires* used to create the network structure was imported and adapted from the model reported in the work by Loeffler, Alon, et al., "Topological properties of neuromorphic nanowire networks", Frontiers in Neuroscience 14 (2020): 184. https://github.com/aloe8475/CODE/blob/master/Analysis/Generate%20Networks/wires.py
