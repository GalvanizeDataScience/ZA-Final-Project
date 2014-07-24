# -*- coding: utf-8 -*-
import graphlab as gl
import networkx as nx
import numpy as np
from community import modularity, partition_at_level
import happy

def __extract_tweets(df):

    twts = df['tweets'].apply(list).tolist()

    twts = [''.join([str(ltr) if ord(ltr) < 128 else '' for ltr in t.strip()])
            for twt in twts for t in twt]

    return twts


def get_topics(df, stops=set(), tweets=None, num=5, alpha=1, beta=0.1):

    if tweets == None:
        tweets = __extract_tweets(df)

    tweets = gl.SArray(data=tweets, dtype=str)

    tweets = tweets.count_words().dict_trim_by_keys(keys=stops)

    model = gl.text.topic_model.create(dataset = tweets, num_topics = num,)
                                       #alpha = alpha, beta = beta)

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


def get_community_analytics(df, graph, num_levels, detail=3):

    stops = gl.text.util.stopwords(lang='en')
    stops.update(['rt', 'http', 'https', 'ly', 'amp', 'don'])
    stops.update(map(str, range(11)))

    data   = {}
    fields = ('topics', 'hashtags', 'mentioned', 'sentiment',
              'density', 'comm_size', 'most_connected')

    for field in fields:
        data[field] = {x:{} for x in range(num_levels)}

    for lvl in range(num_levels):

        col_name = 'cid' + str(lvl)

        num_of_communities = max(df[col_name])

        for cid in xrange(num_of_communities):

            community = df[df[col_name] == cid]
            subgraph = graph.subgraph(community.index.tolist())
            tweets = __extract_tweets(community)

            data['comm_size'][lvl][cid] = community.shape[0]

            data['topics'][lvl][cid] = get_topics(community, stops,
                                                  tweets=tweets, num=detail)

            data['hashtags'][lvl][cid] = get_hashtags(community, num=detail)

            data['mentioned'][lvl][cid] = get_mentions(community, num=detail)

            data['most_connected'][lvl][cid] = get_most_connected(subgraph,
                                                                  num=detail)

            data['density'][lvl][cid] = get_density(subgraph)

            data['sentiment'][lvl][cid] = get_sentiment(community, tweets)

    return data


def get_community_assignment(in_df, graph, dendrogram):

    df = in_df.copy()

    community_modularity = {}

    ctr = len(dendrogram) - 1

    for i in range(len(dendrogram)):

        partition = partition_at_level(dendrogram, i)

        col_name = 'cid' + str(ctr)

        df[col_name] = [partition[ind] for ind in df.index]

        community_modularity[ctr] = modularity(partition, graph)

        ctr -= 1

    return df, community_modularity