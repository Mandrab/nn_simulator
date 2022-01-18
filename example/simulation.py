import progressbar
import random

from main import *

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
    graph, wires_dict = minimum_viable_network(default)

    # save a copy of the created graphs
    backup.save(default, graph, wires_dict, dict())

# select a random ground node
grounds = random_nodes(graph, avoid=set())

# select source nodes from non-grounds nodes
sources = random_nodes(graph, grounds, count=4)

# select output nodes from non-grounds & non-source nodes # todo distance
loads = random_loads(graph, grounds | sources, count=2)

################################################################################
# ELECTRICAL STIMULATION

logger.info('Electrical stimulation of the network')

steps = 90              # simulation duration
pulse_duration = 10     # duration of a stimulation pulse (in steps)
reads = 80              # reads at output
pulse_count = 1         # number of stimulation pulses
delta_t = 0.05          # virtual time delta

v = 10.0                # pulse amplitude of stimulation

# generate vin stimulation for each input
stimulations = [v] * pulse_duration * pulse_count + [0.01] * reads
stimulations = [ [(s, stimulations[i]) for s in sources] for i in range(steps)]

# setup progressbar for print progress
progressbar = progressbar.ProgressBar(max_value=steps)

# growth of the conductive path
logger.debug('Growth of the conductive path')

# initialize network
initialize_graph_attributes(graph, sources, grounds, default.Y_min)
stimulus = voltage_initialization(graph, sources, grounds)

# creation of an analysis utility and save of initial state
evolution = Evolution(default, wires_dict, delta_t, grounds, loads)
evolution.append(graph, stimulus)

# growth over time
for i in range(steps):
    stimulate(graph, default, delta_t, stimulations[i], [*loads], grounds)
    evolution.append(graph, stimulations[i])
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
