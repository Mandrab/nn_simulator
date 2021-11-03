from itertools import product

from model.functions import *


class Data:
    def __init__(
            self,
            device,
            H,
            network_resistant_calculator=calculate_network_resistance
    ):
        M, mapping = device.connected_nodes

        self.source_currents = [
            calculate_source_current(H, mapping[source])
            for source in device.source_nodes
        ]
        self.source_voltages = [
            calculate_source_voltage(H, mapping[source])
            for source in device.source_nodes
        ]

        nx.set_node_attributes(H, nx.information_centrality(M, weight='Y'), "information_centrality")

        # todo does it make sense?
        self.network_resistances = [
            network_resistant_calculator(H, mapping[source])
            for source in device.source_nodes
        ]
        self.network_conductances = [1 / r for r in self.network_resistances]

        # get all source-ground combinations
        paths = product(device.source_nodes, device.ground_nodes)

        self.shortest_paths_length_network = [
            nx.shortest_path_length(
                M,
                source=mapping[path[0]],
                target=mapping[path[1]],
                weight='R'
            ) for path in paths
        ]

        self.information_centrality = nx.get_node_attributes(
            H, 'information_centrality'
        )


def analyse(Hs, device):
    # get all source-ground combinations
    paths = product(device.source_nodes, device.ground_nodes)

    return [Data(device, Hs[0])] + [
        Data(device, H, lambda M, mapping: [
            nx.resistance_distance(
                M,
                mapping[path[0]],
                mapping[path[1]],
                weight='Y',
                invert_weight=False
            ) for path in paths
        ]) for H in {Hs} - {Hs[0]}
    ]
