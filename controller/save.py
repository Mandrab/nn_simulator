
import sys

############################### SAVE DATA #####################################
'''
filename = "nodes_" + str(nwires) + "_junctions_" + str(number_of_edges) + "_seed_"+str(seed)+".txt"
my_data = np.vstack((degrees,clustering))
my_data = my_data.T
np.savetxt(filename,my_data, delimiter = ',', header = 'degree,clustering',comments = '')



###make a graph for gephi
Z = nx.from_numpy_matrix(Adj_matrix)
nx.write_gexf(Z, "test.gexf")

'''
def save():

    #%% Save data (electrical part)
    logging.debug('Data saving')
    timestamp = 0


    #nodes
    pos_el_nodes = nx.get_node_attributes(H_list[timestamp], 'pos')
    x_pos_el = [pos_el_nodes[n][0] for n in H_list[timestamp].nodes]
    y_pos_el = [pos_el_nodes[n][1] for n in H_list[timestamp].nodes]
    V_list_el = [H_list[timestamp].nodes[n]['V'] for n in H_list[timestamp].nodes()]
    Information_centrality_el = [H_list[timestamp].nodes[n]['information_centrality'] for n in H_list[timestamp].nodes()]


    #node file
    filename_el = "Electrical_data_nodes_"+"timestamp = "+str(timestamp)+"_nodes_" + str(nwires) + "_seed_"+str(seed)+".txt"
    my_data_el = np.vstack((x_pos_el,y_pos_el,V_list_el,Information_centrality_el))
    my_data_el = my_data_el.T
    np.savetxt(filename_el,my_data_el, delimiter = ',', header = 'x_pos,y_pos,V_list, Information_centrality_list',comments = '')



    #edges
    pos_el_jx = [H_list[timestamp].edges[u, v]['jx_pos'] for u,v in H_list[timestamp].edges()]
    xj_pos_el = [pos_el_jx[n][0] for n in range(0,len(pos_el_jx))]
    yj_pos_el = [pos_el_jx[n][1] for n in range(0,len(pos_el_jx))]
    I_list_el = [H_list[timestamp].edges[u, v]['I'] for u,v in H_list[timestamp].edges()]
    Y_list_el = [H_list[timestamp].edges[u, v]['Y'] for u,v in H_list[timestamp].edges()]
    g_list_el = [H_list[timestamp].edges[u, v]['g'] for u,v in H_list[timestamp].edges()]

    #edge file
    filename_el_2 = "Electrical_data_edges_"+"timestamp = "+str(timestamp)+"_nodes_" + str(nwires) + "_seed_"+str(seed)+".txt"
    my_data_el_2 = np.vstack((xj_pos_el,yj_pos_el,I_list_el,Y_list_el,g_list_el))
    my_data_el_2 = my_data_el_2.T
    np.savetxt(filename_el_2,my_data_el_2, delimiter = ',', header = 'xj_pos,yj_pos,I_list,Y_list,g_list',comments = '')

    #I-V list
    filename_el_3 = "Electrical_I-V-Y-SP-data_"+"_nodes_" + str(nwires) + "_seed_"+str(seed)+".txt"
    my_data_el_3 = np.vstack((t_list,V_list,I_list,Rnetwork_list,Ynetwork_list,Shortest_path_length_network_list))
    my_data_el_3 = my_data_el_3.T
    np.savetxt(filename_el_3,my_data_el_3, delimiter = ',', header = 't_list,V_list,I_list,Rnetwork_list,Ynetwork_list,Shortest_path_length_network_list',comments = '')
