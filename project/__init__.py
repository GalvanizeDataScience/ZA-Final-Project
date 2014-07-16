# -*- coding: utf-8 -*-
from utils import oauth_login
from data import get_user_data, get_follower_data

API_PATH = '../api_keys/'

def runtime(api_path, screen_name=None, user_id=None):

    apis = oauth_login(API_PATH)

    target_data = get_user_data(apis[0],
                                screen_name=screen_name,
                                user_id=user_id)

    if target_data:
        target, target_tweets, followers, following, user_lists = target_data
    else:
        raise Exception('TargetError')

    data_dict = get_follower_data(apis, followers)
    print len(data_dict.keys())


def thinking_about_this_stuff():
    import networkx as nx
    import community
    #from make_graph import make_graph

    api_path = '../api_keys/'
    screen_name = 'graphlabteam'
    apis = oauth_login(api_path)
    target, target_tweets, followers, following, user_lists = \
        get_user_data(apis[0], screen_name)

    edges = make_graph(target['id'], followers, apis)

    g = nx.Graph(data=edges)

    p0 = community.best_partition(g)
    p1 = community.best_partition(g, partition=p0)

    while p0 != p1:
        p0 = community.best_partition(g, partition=p1)
        p1 = community.best_partition(g, partition=p0)

    partitions = [[k for k in p1.keys() if p1[k] == v]
                     for v in set(p1.values())]

if __name__ == '__main__':
    # screen_name = 'graphlabteam'
    # user_id = None

    # screen_name = 'ZipfianAcademy'
    # user_id = 1244850380

    screen_name = 'Saber_Metrics'
    user_id = None

    runtime(API_PATH, screen_name=screen_name, user_id=user_id)