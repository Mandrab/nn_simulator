import progressbar
import random

from NWNetworkSimulator import *

################################################################################
# SIMULATION SETUP

# set constant seed for simulation
random.seed(1234)

################################################################################
# NETWORK SETUP

# if graph, datasheet and wires backup-files exist, import them
if all(backup.exist()):
    graph, default, wires_dict = backup.read()

# if the backup-files does not exists, create the network and save it
else:
    # create a device that is represented by the given datasheet
    graph, wires_dict = minimum_viable_network(default)

    # save a copy of the created graphs
    backup.save(default, graph, wires_dict)

# select a random ground node
# ground = random_ground(graph)
ground = 358

# select node sources from non-ground nodes
# sources = random_sources(graph, ground, count=4)
sources = [273]

################################################################################
# ELECTRICAL STIMULATION

logging.info('Electrical stimulation of the network')

steps = 90              # simulation duration
pulse_duration = 10     # duration of a stimulation pulse (in steps)
reads = 80              # reads at output
pulse_count = 1         # number of stimulation pulses
delta_t = 0.05          # virtual time delta

v = 10.0                # pulse amplitude of stimulation

# generate vin stimulation for each input
stimulations = [v] * pulse_duration * pulse_count + [0.01] * reads
stimulations = [
    [(source, stimulations[i]) for source in sources]
    for i in range(steps)
]

# setup progressbar for print progress
progressbar = progressbar.ProgressBar(max_value=steps)

# growth of the conductive path
logging.debug('Growth of the conductive path')

# initialize network
initialize_graph_attributes(graph, default.Y_min)
stimulus = voltage_initialization(graph, sources, ground)

# creation of an analysis utility and save of initial state
evolution = Evolution(default, wires_dict, ground, delta_t)
evolution.append(graph, stimulus)

# growth over time
for i in range(1, steps):
    stimulate(graph, default, delta_t, stimulations[i], ground)
    evolution.append(graph, stimulations[i])
    progressbar.update(i+1)

###############################################################################
# ANALYSE & PLOTTING

# inspect(graph)

# plot.plot(evolution, plot.adj_matrix)
# plot.plot(evolution, plot.network)
# plot.plot(evolution, plot.graph)
# plot.plot(evolution, plot.kamada_kawai_graph)
# plot.plot(evolution, plot.degree_of_nodes)
# plot.plot(evolution, plot.highlight_connected_components)
# plot.plot(evolution, plot.largest_connected_component)
# plot.plot(evolution, plot.network_7)
# plot.plot(evolution, plot.conductance)
# plot.plot(evolution, plot.voltage_distribution_map)
# plot.plot(evolution, plot.conductance_map)
# plot.plot(evolution, plot.information_centrality_map)
# plot.plot(evolution, plot.animation)
