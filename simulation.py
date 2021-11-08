import progressbar
import random

from NWNetworkSimulator import *

# set constant seed for simulation
random.seed(1234)

###############################################################################
# NETWORK SETUP

# create a device that is represented by the given datasheet
wires_dict = generate_network(datasheet=default)

# obtain graph representation of the device
graph = get_graph(wires_dict)

# to simplify analysis, take only the largest connected component
# that's ok if there is only one ground; for more grounds also disjoint
# components are ok and may improve functioning: todo hypothesis
graph = largest_component(graph, relabel=True)

# select a random ground node
ground = random.randint(0, graph.number_of_nodes())

# select node sources from non-ground nodes
nodes = [*{*graph.nodes()} - {ground}]
sources = [
    nodes.pop(random.randint(0, len(nodes)))
    for _ in range(4)   # take four sources
]

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
progressbar = progressbar.progressbar(range(steps))

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
    next(progressbar)

###############################################################################
# ANALYSE & PLOTTING

inspect(graph)

plot.plot(evolution, plot.adj_matrix)
plot.plot(evolution, plot.network)
plot.plot(evolution, plot.graph)
plot.plot(evolution, plot.kamada_kawai_graph)
plot.plot(evolution, plot.degree_of_nodes)
plot.plot(evolution, plot.highlight_connected_components)
plot.plot(evolution, plot.largest_connected_component)
plot.plot(evolution, plot.network_7)
plot.plot(evolution, plot.conductance)
plot.plot(evolution, plot.voltage_distribution_map)
plot.plot(evolution, plot.conductance_map)
plot.plot(evolution, plot.information_centrality_map)
plot.plot(evolution, plot.animation)
