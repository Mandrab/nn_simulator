import logging
import networkx as nx

# clustering coefficient list
def __clustering_nodes(G):
    a = nx.clustering(G)
    clustering = []
    for n in range(0, len(a)):
        clustering.append(a[n])

global_statistics = {
    'number of nodes': lambda G: G.number_of_nodes,
    'number of edges (junctions)': lambda G: G.number_of_edges,
    'degree of node': lambda G: [val for (node, val) in G.degree()],
    'clustering of node': __clustering_nodes,
    'number of connected components':
        lambda G: nx.number_connected_components(G),
    'number of isolated nodes': lambda G: len([x for x in nx.isolates(G)]),
    'number of nodes in the largest component':
        lambda G: len(max(nx.connected_components(G), key = len))
}

largest_component_statistics = {
    'diameter of the largest connected component': lambda K: nx.diameter(K),
    'average shortest path length of the largest connected component':
        lambda K: nx.average_shortest_path_length(K, weight = None),
    'average clustering coefficient of the largest connected component':
        lambda K: nx.average_clustering(K),
    'sigma small-world coefficient of the largest connected component':
        lambda K: nx.sigma(K, niter = 100, nrand = 10, seed = None),
    'omega small-world coefficient of the largest connected component':
        lambda K: nx.omega(K, niter = 100, nrand = 10, seed = None)

}

def print_info(key, entity):
    for key_ in global_statistics:
        if key == key_:
            print('The ' + key + ' is:')
            print(global_statistics[key](entity))
    for key_ in largest_component_statistics:
        if key == key_:
            print('The ' + key + ' is:')
            print(largest_component_statistics[key](entity))

def inspect(G):

    for key in global_statistics:
        print('The ' + key + ' is:')
        print(global_statistics[key](G))

    # ANALYSIS OF THE LARGEST CONNECTED COMPONENT

    K = G.copy()
    largest_cc = max(nx.connected_components(G), key = len)
    removed_nodes = [n for n in G.nodes() if n not in largest_cc]
    K.remove_nodes_from(removed_nodes)

    for key in largest_component_statistics:
        print('The ' + key + ' is:')
        print(largest_component_statistics[key](K))


# EXTRACTION OF INFORMATION CENTRALITY
def information_centrality(Hs):
    logging.debug('Evolution of information centrality')

    Information_centrality_list = []

    for H in Hs:
        centrality = nx.get_node_attributes(H,'information_centrality')
        Information_centrality_list.append(list(centrality.values()))

    return Information_centrality_list
