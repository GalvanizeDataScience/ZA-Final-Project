# -*- coding: utf-8 -*-
import networkx as nx
import matplotlib.pyplot as plt
import community


# Source: https://www.udacity.com/wiki/creating-network-graphs-with-python
def draw_nx_graph(G, labels=None, graph_layout='shell',
               node_size=200, node_color='blue', node_alpha=0.3,
               node_text_size=12,
               edge_color='blue', edge_alpha=0.3, edge_thickness=1,
               edge_text_pos=0.3,
               text_font='sans-serif'):

    # these are different layouts for the network you may try
    # shell seems to work best
    if graph_layout == 'spring':
        graph_pos = nx.spring_layout(G)
    elif graph_layout == 'spectral':
        graph_pos = nx.spectral_layout(G)
    elif graph_layout == 'random':
        graph_pos = nx.random_layout(G)
    else:
        graph_pos = nx.shell_layout(G)

    # draw graph
    nx.draw_networkx_nodes(G, graph_pos, node_size=node_size,
                           alpha=node_alpha, node_color=node_color)

    nx.draw_networkx_edges(G, graph_pos, width=edge_thickness,
                           alpha=edge_alpha, edge_color=edge_color)

    nx.draw_networkx_labels(G, graph_pos, font_size=node_text_size,
                            font_family=text_font)

    # if labels is None:
    #    labels = G.nodes()
    # edge_labels = dict(zip(G.edges(), labels))
    # nx.draw_networkx_edge_labels(G, graph_pos)

    plt.show()


def get_pagerank(g):
    return nx.pagerank(g)


def get_partitions(g, optimize=True):

    p0 = community.best_partition(g)

    if not optimize:
        return p0

    p1 = community.best_partition(g, partition=p0)

    while p0 != p1:
        p0 = community.best_partition(g, partition=p1)
        p1 = community.best_partition(g, partition=p0)

    return p1


def make_graph(df, similarity_matrix=None):

    g = nx.Graph()

    for i, user1_id in enumerate(df.index[:-1]):
        for j, user2_id in enumerate(df.index[i+1:]):
            if similarity_matrix != None:
                if similarity_matrix[i,j] > 0:
                    g.add_edge(user1_id, user2_id,
                               weight=similarity_matrix[i,j])
            else:
                g.add_edge(user1_id, user2_id, weight=1)

    return g