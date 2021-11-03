from NWNetworkSimulator import *

import progressbar

###############################################################################
# NETWORK SETUP

# create a device that is represented by the given datasheet
device = Device(
    datasheet=default,
    source_nodes=[273],
    ground_nodes=[358],
)

###############################################################################
# ELECTRICAL STIMULATION

logging.info('Electrical stimulation of the network')

timesteps = 90          # simulation duration
pulse_duration = 10     # duration of a stimulation pulse (in timesteps)
reads = 80              # reads at output
pulse_count = 1         # number of stimulation pulses
delta_t = 0.05          # virtual time delta

v = 10.0                # pulse amplitude of stimulation

# generate vin stimulation for each input
stimulations = [v] * pulse_duration * pulse_count + [0.01] * reads
stimulations = [[(source, stimulations[i]) for source in device.source_nodes] for i in range(timesteps)]

# setup progressbar for print progress
progressbar = progressbar.progressbar(range(timesteps))

# growth of the conductive path
logging.debug('Growth of the conductive path')

# pristine state - create stimulator that initialize the state (todo ?)
stimulator = Stimulator(device=device, datasheet=default)

# growth over time
for i in range(timesteps):
    stimulator.stimulate(stimulations[i])
    next(progressbar)

###############################################################################
# ANALYSE & PLOTTING

#inspect(device.graph)
#plot.plot(device, default, plot.network)
