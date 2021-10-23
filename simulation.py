from NWNetworkSimulator import *

import progressbar

###############################################################################
# NETWORK SETUP

connections = devices.generate(device=default)
graph = devices.get_graph(connections)

###############################################################################
# ELECTRICAL STIMULATION

logging.info('Electrical stimulation of the network')

timesteps = 90          # simulation duration
pulse_duration = 10     # duration of a stimulation pulse (in timesteps)
reads = 80              # reads at output
pulse_count = 1         # number of stimulation pulses
delta_t = 0.05          # virtual time delta

v = 10.0                # pulse amplitude of stimulation

# stimulate for 10 timesteps and then rest
Vins = [v] * pulse_duration * pulse_count + [0.01] * reads

# setup progressbar for print progress
progressbar = progressbar.progressbar(range(timesteps))

# growth of the conductive path
logging.debug('Growth of the conductive path')

# pristine state - create stimulator that initialize the state (todo ?)
stimulator = NetworkStimulator(graph, device=default)

# growth over time
for i in range(timesteps):
    stimulator.stimulate(default.sourcenode, default.groundnode, Vins[i])
    next(progressbar)

information_centrality(stimulator.H)

###############################################################################
# PLOTTING

#inspect(graph)
#plot.plot(lambda: plot.adj_matrix(connections))
