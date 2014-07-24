# -*- coding: utf-8 -*-
import pymongo
import pickle
import os
from utils import oauth_login
from data import get_user_data, get_follower_data
from parse import filter_dataframe, parse_dataframe
from similarity import make_similarity_dataframe
from graph import make_graph
from community import generate_dendrogram
from community_analytics import (get_community_assignment,
                                 get_community_analytics)
from conversions import get_screen_names

API_PATH = '../api_keys/'
PKL_PATH = '../pickles/'
DB_NAME = 'twitter'

def load_info_for(screen_name=None, user_id=None,
                  force_db_update = False, force_twitter_update=False):

    if screen_name == None and user_id == None:
        raise Exception('Please enter an id or name')

    sn_file = PKL_PATH + str(screen_name) + '.pkl'
    id_file = PKL_PATH + str(user_id) + '.pkl'

    if os.path.isfile(sn_file) and not force_db_update:
        return pickle.load(open(sn_file, 'rb'))

    if os.path.isfile(id_file) and not force_db_update:
        return pickle.load(open(id_file, 'rb'))

    apis = oauth_login(API_PATH)

    try:
        conn = pymongo.MongoClient("localhost", 27017)

    except pymongo.errors.ConnectionFailure:
        print 'Please run mongod and re-run program'
        raise Exception('DBError')

    db = conn[DB_NAME]

    user_data = get_user_data(db, apis[0], name=screen_name, uid=user_id)

    if user_data == None:
        print 'Was unable to access data for %s / %s' % (screen_name, user_id)
        raise Exception('TargetError')

    user_info, user_tweets, followers, following, user_lists = user_data

    raw_df = get_follower_data(db, apis, followers)

    df = parse_dataframe( filter_dataframe(raw_df) )

    del raw_df

    df_similarity = make_similarity_dataframe(df)

    graph = make_graph(df, df_similarity)

    dendrogram = generate_dendrogram(graph)

    del df_similarity

    df, modularity = get_community_assignment(df, graph, dendrogram)

    num_levels = len(dendrogram)

    data = get_community_analytics(df, graph, num_levels)

    data['mentioned'] = get_screen_names(data['mentioned'], df, db, apis[0])

    data['most_connected'] = get_screen_names(data['most_connected'],
                                              df, db, apis[0])

    conn.close()

    # dump all those things into a pickle
    pickle.dump((df, graph, dendrogram, data), open(sn_file, 'wb'))

    # return all of those things
    return df, graph, dendrogram, data

#------------------------------
# screen_name = 'graphlabteam'
# user_id = 1447135560
#------------------------------
# screen_name = 'ZipfianAcademy'
# user_id = 1244850380
#------------------------------
screen_name = 'Saber_Metrics'
user_id = 625183821
#------------------------------
# screen_name = 'stripe'
# user_id = None
#------------------------------
# screen_name = 'coinbase'
# user_id = None
#------------------------------

df, graph, dendrogram, data = load_info_for(screen_name)
print data['most_connected']

#   TODO
    # implement update logic that forcefully pulls data from twitter
    # do i need to get subgraphs? // simplified graphs where community = node?

    # visualize using pretty carto graphs
    # convert topics to word map thing