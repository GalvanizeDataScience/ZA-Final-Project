# -*- coding: utf-8 -*-
import graphlab as gl
import networkx as nx
import numpy as np
from community import modularity, partition_at_level
import happy
import d3py

def __extract_tweets(df):

    twts = df['tweets'].apply(list).tolist()

    twts = [''.join([str(ltr) if ord(ltr) < 128 else '' for ltr in t.strip()])
            for twt in twts for t in twt]

    return twts


def get_topics(df, stops=set(), tweets=None, num=5):

    if tweets == None:
        tweets = __extract_tweets(df)

    tweets = gl.SArray(data=tweets, dtype=str)

    tweets = tweets.count_words().dict_trim_by_keys(keys=stops)

    model = gl.text.topic_model.create(dataset = tweets, num_topics = num)

    topics = model.get_topics(range(num))

    topics = topics.apply(lambda x: x.values()).astype(list)

    result = {}
    for i in range(num):
        result[i] = [(x[2], x[1]) for x in topics if x[0] == i]

    return result


def get_hashtags(df, num=5):

    hashtags = reduce(lambda x, y: x + y, df['hashtags'].apply(list).tolist())

    hashtags = [''.join([str(x).lower() if ord(x) < 128 else '' for x in ht])
                for ht in hashtags]

    hashtags = sorted([(hashtags.count(x), '#' + x) for x in set(hashtags)],
                      reverse=True)

    return [x[1] for x in hashtags[:num]]


def get_mentions(df, num=5):

    mentions = reduce(lambda x, y: x + y, df['mentions'].apply(list).tolist())

    mentions = sorted([(mentions.count(x), x) for x in set(mentions)],
                      reverse=True)

    return [x[1] for x in mentions[:num]]


def get_density(subgraph):

    return nx.density(subgraph)


def get_most_connected(subgraph, num=5):

    try:
        pr = nx.pagerank(subgraph)

    except nx.exception.NetworkXError:
        return None

    pr = sorted([(val, user) for user, val in pr.iteritems()], reverse=True)

    return [x[1] for x in pr[:num]]


def get_sentiment(df, tweets=None):

    if tweets == None:
        tweets = __extract_tweets(df)

    sentiments = happy.hi(tweets)

    return np.mean(sentiments), np.std(sentiments)


def get_community_analytics(df, graph, num_levels, detail=3,
                            community_modularity=None):

    stops = gl.text.util.stopwords(lang='en')

    # extra stop words, mostly for rt, url links, unicode, and compound words
    stops.update(['rt', 'http', 'https', 'ly', 'amp', 'don', 'wasn', 're',
                  'aren', 'didn', 'how', 'nt', 'co', 've', 'gt', 'll',
                  'bit'])
    # get rid of arbitrary single numbers
    stops.update(map(str, range(11)))


    data = {x:{} for x in range(num_levels)}

    for lvl in xrange(num_levels):

        col_name = 'cid' + str(lvl)

        num_of_communities = max(df[col_name])

        for cid in xrange(num_of_communities + 1): # +1 for inclusive rng

            if cid not in data[lvl]:
                data[lvl][cid] = {}

            subdf = df[df[col_name] == cid]

            subgraph = graph.subgraph(subdf.index.tolist())

            tweets = __extract_tweets(subdf)

            data[lvl][cid]['comm_size'] = subdf.shape[0]

            data[lvl][cid]['topics'] = get_topics(subdf, stops,
                                                  tweets=tweets, num=detail)

            data[lvl][cid]['hashtags'] = get_hashtags(subdf, num=detail)

            data[lvl][cid]['mentioned'] = get_mentions(subdf, num=detail)

            data[lvl][cid]['most_connected'] = get_most_connected(subgraph,
                                                                  num=detail)

            data[lvl][cid]['density'] = get_density(subgraph)

            data[lvl][cid]['sentiment'] = get_sentiment(subdf, tweets)

            if community_modularity != None:
                data[lvl][cid]['modularity'] = community_modularity[lvl]
            else:
                data[lvl][cid]['modularity'] = None

    return data


def get_community_assignment(in_df, graph, dendrogram):

    df = in_df.copy()

    community_modularity = {}

    for i in range(len(dendrogram)):

        partition = partition_at_level(dendrogram, i)

        df['cid' + str(i)] = [partition[ind] for ind in df.index]

        community_modularity[i] = modularity(partition, graph)

    return df, community_modularity


def create_community_graph(user_info, data, dendrogram):

    g = nx.Graph()

    sn = user_info['id']

    fields = ('followers_count', 'friends_count', 'id', 'name', 'description')

    root_node = {k:v for k,v in user_info if k in fields}

    g.add_node(sn, attr_dict=user_info)

    for i in data:

        dmap = None if i + 1 >= len(dendrogram) else dendrogram[i + 1]

        for j in data[i]:

            child_node = str(i) + '-' + str(j)
            g.add_node(child_node, attr_dict=data[i][j])

            parent_node = sn if dmap == None else str(i+1) +'-'+ str(dmap[j])
            g.add_edge(child_node, parent_node)

    return g


def create_community_json(graph):
    return d3py.json_graph.node_link_data(graph)
    #return nx.readwrite.json_graph.node_link_data(graph)