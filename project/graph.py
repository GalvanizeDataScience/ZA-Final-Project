# -*- coding: utf-8 -*-
import networkx as nx

def make_graph(df, df_similarity=None):

    g = nx.Graph()

    try:
        use_weights = df_similarity == None

    except:
        use_weights = True

    for i, user1_id in enumerate(df.index[:-1]):

        for user2_id in df.index[i+1:]:

            if use_weights:

                if df_similarity.ix[user1_id, user2_id] > 0:

                    g.add_edge(user1_id, user2_id,
                               weight=df_similarity.ix[user1_id, user2_id])

            else:
                g.add_edge(user1_id, user2_id, weight=1)

    return g