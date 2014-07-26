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


def create_community_graph(data, dendrogram):

    g = nx.DiGraph()

    for i in data:

        dmap = None if i + 1 >= len(dendrogram) else dendrogram[i + 1]

        for j in data[i]:

            child_node = str(i) + '-' + str(j)
            g.add_node(child_node, attr_dict=data[i][j])

            g.node[child_node]['name'] = child_node
            g.node[child_node]['group'] = i

            if dmap != None:
                parent_node = str(i+1) +'-'+ str(dmap[j])
                g.add_edge(child_node, parent_node)
                g.edge[child_node][parent_node]['value'] = 1

    return g


def create_community_json(graph, user_info):

    community_json = d3py.json_graph.node_link_data(graph)

    # Add user information info to the json file
    community_json['root'] = {}
    community_json['root']['id_'] = user_info['id']
    community_json['root']['screen_name'] = user_info['screen_name']
    community_json['root']['name_'] = user_info['name']
    community_json['root']['description'] = user_info['description']
    community_json['root']['friends_count'] = user_info['friends_count']
    community_json['root']['followers_count'] = user_info['followers_count']

    return community_json