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
                                 get_community_analytics,
                                 create_community_graph,
                                 create_community_json)
from conversions import get_screen_names

API_PATH = '../api_keys/'
PKL_PATH = '../pickles/'
DB_NAME = 'twitter'


def load_info_for(screen_name=None, user_id=None,
                  force_db_update = False, force_twitter_update=False,
                  debug=False):

    if screen_name == None and user_id == None:
        raise Exception('Please enter an id or name')

    # Check to see if there are pickles for the user. Note that this will be
    # overriden
    sn_file = PKL_PATH + str(screen_name) + '.pkl'
    sn_file_debug = PKL_PATH + str(screen_name) + '_debug.pkl'

    if os.path.isfile(sn_file_debug) and not force_db_update and debug:
        return pickle.load(open(sn_file_debug, 'rb'))

    if os.path.isfile(sn_file) and not force_db_update:
        return pickle.load(open(sn_file, 'rb'))

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

    df_similarity = make_similarity_dataframe(df)

    graph = make_graph(df, df_similarity)

    dendrogram = generate_dendrogram(graph)

    df, modularity = get_community_assignment(df, graph, dendrogram)

    num_levels = len(dendrogram)

    data = get_community_analytics(df, graph, num_levels,
                                   community_modularity = modularity)

    data = get_screen_names(data, 'mentioned', df, db, apis[0])

    data = get_screen_names(data, 'most_connected', df, db, apis[0])

    conn.close()

    community_graph = create_community_graph(user_info, data, dendrogram)

    community_json = create_community_json(community_graph)

    pickle.dump((raw_df, df, df_similarity, dendrogram, data,
                 community_graph, community_json), open(sn_file_debug, 'wb'))

    pickle.dump(community_json, open(sn_file, 'wb'))

    if debug:
        return (raw_df, df, df_similarity, dendrogram, data,
                community_graph, community_json)

    return community_json

#------------------------------
screen_name = 'graphlabteam'
user_id = 1447135560
#------------------------------
# screen_name = 'ZipfianAcademy'
# user_id = 1244850380
#------------------------------
# screen_name = 'Saber_Metrics'
# user_id = 625183821
#------------------------------
# screen_name = 'stripe'
# user_id = None
#------------------------------
# screen_name = 'coinbase'
# user_id = None
#------------------------------

data = load_info_for(screen_name)

#   TODO
    # implement update logic that forcefully pulls data from twitter
    # get community-based node-graph thing -- with attributes?
    # graph -> json?
