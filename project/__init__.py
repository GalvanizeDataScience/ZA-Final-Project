# -*- coding: utf-8 -*-
from utils import oauth_login
from data import get_user_data, get_follower_data
from graph import make_graph

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

    df = get_follower_data(apis, followers, parse_data=True, as_df=True)

    graph, partitions = get_graph(df, partitions=True, optimize=True)


if __name__ == '__main__':
    # screen_name = 'graphlabteam'
    # user_id = None

    # screen_name = 'ZipfianAcademy'
    # user_id = 1244850380

    screen_name = 'Saber_Metrics'
    user_id = None

    runtime(API_PATH, screen_name=screen_name, user_id=user_id)