# -*- coding: utf-8 -*-
import pymongo
from utils import oauth_login
from data import get_user_data, get_follower_data
from graph import make_graph, get_partitions
from filter import filter_user_dataframe
from similarity import build_similarity_matrix

API_PATH = '../api_keys/'
DB_NAME = 'twitter'

if __name__ == '__main__':

    #screen_name = 'graphlabteam'
    #user_id = None

    # screen_name = 'ZipfianAcademy'
    # user_id = 1244850380

    #screen_name = 'Saber_Metrics'
    #user_id = None

    screen_name = 'stripe'
    user_id = None

    apis = oauth_login(API_PATH)

    try:
        db = pymongo.MongoClient("localhost", 27017)[DB_NAME]
    except pymongo.errors.ConnectionFailure:
        print 'Please run mongod and re-run program'
        import sys
        sys.exit(0)


    target_data = get_user_data(db, apis[0], name=screen_name, id=user_id)

    if target_data:
        target, target_tweets, followers, following, user_lists = target_data
    else:
        print 'Was unable to access data for %s / %s' % (screen_name, user_id)
        raise Exception('TargetError')

    # existing_cache = db.data.find({'id': {'$in': followers}})

    ## put existing_cache into play

    user_df = get_follower_data(db, apis, followers, start=3770, sleeper=45)

    user_df = filter_user_dataframe(user_df)

    user_similarity = build_similarity_matrix(user_df)

    graph = make_graph(user_df, user_similarity)

    partitions = get_partitions(graph, optimize=True)

    #graphs = partition_graph(graph, partitions)