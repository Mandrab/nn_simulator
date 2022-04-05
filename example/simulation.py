import progressbar
import random

from nn_simulator import *
from nn_simulator.logger import logger


################################################################################
# SIMULATION SETUP

# set constant seed for simulation
random.seed(1234)

################################################################################
# NETWORK SETUP

# if graph, datasheet and wires backup-files exist, import them
if all(backup.exist()):
    graph, default, wires_dict, _ = backup.read()

# if the backup-files does not exists, create the network and save it
else:
    # create a device that is represented by the given datasheet
    wires_dict = generate_network_data(default)
    graph = nanowire_network(wires_dict, default.Y_min)

    # save a copy of the created graphs
    backup.save(default, graph, wires_dict, dict())

# select source nodes from non-grounds nodes
sources = random_nodes(graph, set(), count=4)

# select output nodes from non-grounds & non-source nodes # todo distance
loads = random_loads(graph, sources, count=2)

for load, resistance in loads.items():
    connect(graph, load, resistance)

################################################################################
# ELECTRICAL STIMULATION

logger.info('Electrical stimulation of the network')

steps = 90              # simulation duration
pulse_duration = 10     # duration of a stimulation pulse (in steps)
reads = steps - pulse_duration  # reads at output
pulse_count = 1         # number of stimulation pulses
delta_t = 0.05          # virtual time delta

v = 10.0                # pulse amplitude of stimulation

# generate vin stimulation for each input
stimulation = [v] * pulse_duration * pulse_count + [0.01] * reads
stimulation = [[(s, stimulation[i]) for s in sources] for i in range(steps)]

# setup progressbar for print progress
progressbar = progressbar.ProgressBar(max_value=steps)

# growth of the conductive path
logger.debug('Growth of the conductive path')

# creation of an analysis utility and save of initial state
evolution = Evolution(default, wires_dict, delta_t, loads)

# growth over time
for i in range(steps):
    stimulate(graph, default, delta_t, dict(stimulation[i]))
    evolution.append(graph, dict(stimulation[i]))
    progressbar.update(i+1)
progressbar.finish()

###############################################################################
# ANALYSE & PLOTTING

# inspect(graph)

# plot.plot(evolution, plot.adjacency_matrix).show()
# plot.plot(evolution, plot.nanowires_distribution).show()
# plot.plot(evolution, plot.enumerated_nanowires_distribution).show()
# plot.plot(evolution, plot.graph_of_the_network_Kamada_Kawai).show()
# plot.plot(evolution, plot.degree_of_nodes_histogram).show()
# plot.plot(evolution, plot.connected_components).show()
# plot.plot(evolution, plot.labeled_network).show()
# plot.plot(evolution, plot.largest_connected_component).show()
# plot.plot(evolution, plot.network_conductance).show()
# plot.plot(evolution, plot.voltage_distribution).show()
# plot.plot(evolution, plot.conductance_distribution).show()
# plot.plot(evolution, plot.information_centrality).show()
# plot.plot(evolution, plot.outputs).show()
# plot.plot(evolution, plot.animation).show()
# plot.plot(evolution, plot.animation_kamada_kawai).show()
