import logging
import progressbar

from model.functions import *
from model.network.utils import modified_voltage_node_analysis


class Stimulator():
    __bar = progressbar.ProgressBar(max_value=progressbar.UnknownLength)
    __counter = 0
    __close_step = lambda _: None

    time = 0
    H = []

    def __init__(self, device, datasheet, delta_time=0.05):
        self.device = device
        self.datasheet = datasheet
        self.delta_time = delta_time

        # initialize the network through an initial stimulation
        self.update_edge_weights = lambda *_: None
        self.stimulate(
            # set connector voltage to 0.01 for each source
            map(lambda source: (source, 0.01), device.source_nodes)
        )
        self.update_edge_weights = update_edge_weights

    def enable_progress_print(self):
        self.__close_step = lambda: self.__bar.update(self.__counter)

    # STIMULATE THE NETWORK WITH THE GIVEN INPUT ON THE CORRESPONDING PIN
    def stimulate(self, inputs):
        logging.debug(f'Electrical stimulation of the network. Virtual time: %.2f' % self.time)

        # update weight of the edges. ignored at first round
        self.update_edge_weights(self.device, self.datasheet, self.delta_time)

        # update voltage values of the nodes of the system after the stimulation
        H = modified_voltage_node_analysis(self.device, inputs)
        self.H.append(H)

        # todo for plotting?
        # nx.set_node_attributes(
        #     H,
        nx.information_centrality(self.device.connected_nodes[0], weight='Y'),# todo: needed for functioning?
        #     "information_centrality"
        # )

        self.__counter += 1
        self.__close_step()
        self.time += self.delta_time
