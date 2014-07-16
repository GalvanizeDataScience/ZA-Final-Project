# -*- coding: utf-8 -*-
import twitter
import time
from cache import get_cache, make_cache
from parse import parse_user_data

URLS = ('url', 'urls')

def __traverse(in_dict, lookup):
    d = in_dict.copy()
    for k, v in d.iteritems():
        if k in lookup and type(v) == dict:
            d[k] = d[k].items()
        elif type(v) == dict:
            d[k] = __traverse(v, lookup)
    return d


def get_user_info(api, user_id=None, screen_name=None):
    '''
    api: twitter.Api oauth login object
    user_id: twitter user id as integer (Optional)
    screen_name: twitter screen name as string (Optional)

    return: twitter.user object
    '''

    if user_id:
        user_info = get_cache(user_id, 'info', 'json')

        if user_info == None:
            user_info = api.GetUser(user_id=user_id).AsDict()
            user_info = __traverse(user_info, ('url', 'urls'))
            make_cache(user_info, user_info['id'], 'info', 'json')

    else:
        user_info = api.GetUser(screen_name=screen_name).AsDict()
        user_info = __traverse(user_info, URLS)
        make_cache(user_info, user_info['id'], 'info', 'json')

    return user_info


def get_user_tweets(api, user_id):
    '''
    api: twitter.Api oauth login object
    user_id: twitter user id as integer

    return: List of integer ids following the user_id
    '''
    tweets = get_cache(user_id, 'tweets', 'jsonlist')

    if tweets == None:
        tweets = api.GetUserTimeline(user_id = user_id,
                                     count = 200,
                                     trim_user = True)
        tweets = [__traverse(tweet.AsDict(), URLS) for tweet in tweets]
        make_cache(tweets, user_id, 'tweets', 'jsonlist')

    return tweets


def get_user_followers(api, user_id):
    '''
    api: twitter.Api oauth login object
    user_id: twitter user id as integer

    return: List of integer ids following the user_id
    '''

    followers = get_cache(user_id, 'followers', 'csv')

    if followers == None:
        followers = api.GetFollowerIDs(user_id = user_id)
        make_cache(followers, user_id, 'followers', 'csv')

    return followers


def get_user_following(api, user_id):
    '''
    api: twitter.Api oauth login object
    user_id: twitter user id as integer

    return: List of integer ids following the user_id
    '''

    following = get_cache(user_id, 'following', 'csv')

    if following == None:
        following = api.GetFriendIDs(user_id = user_id)
        make_cache(following, user_id, 'following', 'csv')

    return following


def get_user_lists(api, user_id=None, screen_name=None):
    '''
    api: twitter.Api oauth login object
    user_id: twitter user id as integer (Optional)
    screen_name: twitter screen name as string (Optional)

    return: twitter.user object
    '''

    user_lists = get_cache(user_id, 'list', 'jsonlist')

    if user_lists == None:
        user_lists = api.GetListsList(None, user_id=user_id)
        user_lists = [__traverse(ul.AsDict(), URLS) for ul in user_lists]
        make_cache(user_lists, user_id, 'list', 'jsonlist')

    return user_lists


def get_user_data(api, screen_name=None, user_id=None, ctr=0):
    '''
    :param api:
    :param screen_name:
    :param user_id:
    :param ctr:
    :return:
    '''

    try:

        target = get_user_info(api, screen_name=screen_name, user_id=user_id)
        tweets = get_user_tweets(api, user_id=target['id'])
        user_lists = get_user_lists(api, user_id=target['id'])

        if 'followers_count' in target:
            if target['followers_count'] > 50000:
                followers = 'Many'
            else:
                followers = get_user_followers(api, user_id=target['id'])
        else:
            followers = get_user_followers(api, user_id=target['id'])

        if 'friends_count' in target:
            if target['friends_count'] > 50000:
                following = 'Many'
            else:
                following = get_user_following(api, user_id=target['id'])
        else:
            following = get_user_following(api, user_id=target['id'])

        return target, tweets, followers, following, user_lists

    except (twitter.error.TwitterError, twitter.TwitterError) as err:
        if str(err)[0:3] == 'Not' or ctr > 15:
            print 'User is protected:', user_id

        elif '63' in str(err):
            print 'User has been suspended:', user_id

        elif '88' in str(err):
            print 'Rate Limit reached on:', user_id
            ctr += 1
            time.sleep(60)
            return get_user_data(api,
                                 screen_name = screen_name,
                                 user_id = user_id,
                                 ctr = ctr)
        else:
            print err

        return None


def get_follower_data(apis, followers, parse_data=False, as_df=False):
    '''
    apis:
    followers:
    return:
    '''

    num_apis = len(apis)

    num_followers = len(followers)

    result = {}

    for ind, id in enumerate(followers):

        print ind, 'of', num_followers, '. On id:', id

        n = ind % num_apis

        user_data = get_user_data(apis[n], user_id=id)

        if parse_data:
            result[id] = parse_user_data(user_data)

        else:
            uinfo, utweets, ufollowers, ufollowing, ulists = user_data
            result[id] = {'info': uinfo,
                          'tweets': utweets,
                          'followers': ufollowers,
                          'following': ufollowing,
                          'lists': ulists}

    if parse_data and as_df:
        import pandas as pd
        return pd.DataFrame(data=result)

    return result