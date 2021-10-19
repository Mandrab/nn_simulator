from NWNetworkSimulator import *

###############################################################################
# NW DISTRIBUTION PARAMETERS

nwires = 900#1500
centroid_dispersion = 200

mean_length = 40.0
std_length = 14.0
seed = 40

# todo non constant
Lx = 500
Ly = 500

##Source and ground node positions
sourcenode = 273                                                  
groundnode = 358

# update_edge_weights parameters

kp0 = 0.0001
eta_p = 10
kd0 = 0.5
eta_d = 1

# admittance
Y_min = 0.001                                                                  
Y_max = Y_min*100

###############################################################################
# NETWORK SETUP

connections = NetworkUtils.generate(
    nwires,
    mean_length,
    std_length,
    centroid_dispersion,
    seed,
    Lx,
    Ly
)

graph = NetworkUtils.get_graph(connections)

###############################################################################
# ELECTRICAL STIMULATION

logging.info('Electrical stimulation of the network')

timesteps = 90          # simulation duration
pulse_duration = 10     # duration of a stimulation pulse (in timesteps)
reads = 80              # reads at output
pulse_count = 1         # number of stimulation pulses
delta_t = 0.05          # virtual time delta

v = 10                  # pulse amplitude of stimulation

# stimulate for 10 timesteps and then rest
Vins = [0.01] + [v] * pulse_duration * pulse_count + [0.01] * reads

# growth of the conductive path
logging.info('Growth of the conductive path')

# pristine state - create stimulator that initialize the state (todo ?)
stimulator = NetworkStimulator(graph, Y_min)

# growth over time
for i in range(0, int(timesteps)):
    stimulator.stimulate(sourcenode, groundnode, Vins[i])

information_centrality(stimulator.H)

###############################################################################
# PLOTTING

#inspect(graph)
plot.plot(lambda: plot.adj_matrix(connections))
