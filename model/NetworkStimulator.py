from functools import cache
from model.functions import *

import logging
import networkx as nx

PATH_ERROR = 'Source and ground node are NOT connected! Stimulation is not possible!'

class NetworkStimulator():

    time = 0
    delta_time = 0.05
    H = []

    def __init__(self, graph, min_admittance):
        self.graph = graph
        self.min_admittance = min_admittance    # previously Y_min

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

        M = initialize_graph_attributes(M, self.min_admittance)

        M.nodes[mapping[sourcenode]]['source_node'] = True
        M.nodes[mapping[groundnode]]['ground_node'] = True

        return M, mapping

    @cache
    def __information_centrality(self, M):
        return nx.information_centrality(M, weight = 'Y')

    def stimulate(self, sourcenode, groundnode, v_in):

        assert nx.has_path(self.graph, sourcenode, groundnode), PATH_ERROR

        # retrieve connected nodes (cached)
        M, mapping = self.__connected_nodes(sourcenode, groundnode)

        logging.debug(f'Electrical stimulation of the network. Virtual time: %.2f' % self.time)

        H = mod_voltage_node_analysis(
            M,
            v_in,
            mapping[sourcenode],
            mapping[groundnode]
        )
        self.H.append(H)

        I = calculate_Isource(H, mapping[sourcenode])
        V = calculate_Vsource(H, mapping[sourcenode])

        nx.set_node_attributes(
            H,
            self.__information_centrality(M),
            "information_centrality"
        )

        # Rnetwork = calculate_network_resistance(H, mapping[sourcenode]) \
        #     if time == 0 else \
        #         nx.resistance_distance(
        #             M,
        #             mapping[sourcenode],
        #             mapping[groundnode],
        #             weight = 'Y',
        #             invert_weight = False
        #         )
        # Ynetwork = 1/Rnetwork

        # Shortest_path_length_network = nx.shortest_path_length(
        #     M,
        #     source = mapping[sourcenode],
        #     target = mapping[groundnode],
        #     weight = 'R'
        # )

        self.time += self.delta_time
