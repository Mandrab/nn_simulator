from functools import cache
from model.functions import *

import logging
import networkx as nx
import progressbar

PATH_ERROR = 'Source and ground node are NOT connected! Stimulation is not possible!'


class NetworkStimulator():
    __bar = progressbar.ProgressBar(max_value=progressbar.UnknownLength)
    __counter = 0
    __close_step = lambda _: None

    time = 0
    H = []

    def __init__(self, graph, device, delta_time=0.05):
        self.graph = graph
        self.device = device
        self.delta_time = delta_time
        self.M, self.mapping = self.__connected_nodes(
            device.sourcenode,
            device.groundnode
        )   # retrieve connected nodes (cached operation)
        self.update_edge_weigths = lambda *_: None
        self.stimulate(device.sourcenode, device.groundnode, 0.01)  # first stimulation is an initialization
        self.update_edge_weigths = update_edge_weigths

    def enable_progress_print(self):
        self.__close_step = lambda: self.__bar.update(self.__counter)

    @cache
    def __is_stimulable(self, sourcenode, groundnode):
        return nx.has_path(self.graph, sourcenode, groundnode)

    @cache
    def __connected_nodes(self, sourcenode, groundnode):

        # select connected graph (between source and ground node)
        logging.debug('Get nodes connected to source and ground')

        M = self.graph.copy()

        # remove nodes not connected to the groundnode (and sourcenode)
        removed_nodes = [n for n in self.graph.nodes()
            if not nx.has_path(self.graph, n, groundnode)]
        M.remove_nodes_from(removed_nodes)

        nodes_count = M.number_of_nodes()

        # relable node names (for mod_voltage node analysis)
        mapping = dict(zip(M, range(0, nodes_count)))
        M = nx.relabel_nodes(M, mapping)

        M = initialize_graph_attributes(M, self.device.Y_min)

        M.nodes[mapping[sourcenode]]['source_node'] = True
        M.nodes[mapping[groundnode]]['ground_node'] = True

        return M, mapping

    def stimulate(self, sourcenode, groundnode, v_in):

        # source and ground have to be connected (cached operation)
        if not self.__is_stimulable(sourcenode, groundnode):
            return logging.error(PATH_ERROR)

        logging.debug(f'Electrical stimulation of the network. Virtual time: %.2f' % self.time)

        # update weight of the edges. ignore at first round
        self.update_edge_weigths(
            self.M,
            self.delta_time,
            self.device.Y_min, self.device.Y_max,
            self.device.kp0, self.device.eta_p,
            self.device.kd0, self.device.eta_d
        )

        H = mod_voltage_node_analysis(
            self.M,
            v_in,
            self.mapping[sourcenode],
            self.mapping[groundnode]
        )
        self.H.append(H)

        # todo for plotting
        # I = calculate_Isource(H, self.mapping[sourcenode])
        # V = calculate_Vsource(H, self.mapping[sourcenode])

        # todo for plotting
        # nx.set_node_attributes(
        #     H,
        nx.information_centrality(self.M, weight='Y'),
        #     "information_centrality"
        # )

        # todo for plotting
        # Rnetwork = calculate_network_resistance(H, self.mapping[sourcenode]) \
        #     if time == 0 else \
        #         nx.resistance_distance(
        #             self.M,
        #             self.mapping[sourcenode],
        #             self.mapping[groundnode],
        #             weight = 'Y',
        #             invert_weight = False
        #         )
        # Ynetwork = 1/Rnetwork

        # Shortest_path_length_network = nx.shortest_path_length(
        #     self.M,
        #     source = self.mapping[sourcenode],
        #     target = self.mapping[groundnode],
        #     weight = 'R'
        # )

        self.__counter += 1
        self.__close_step()
        self.time += self.delta_time
