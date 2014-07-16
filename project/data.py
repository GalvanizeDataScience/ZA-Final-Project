# -*- coding: utf-8 -*-
import twitter
import time
from cache import get_cache, make_cache

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
            make_cache(user_info, user_info['id'], 'info', 'json')

    else:
        user_info = api.GetUser(screen_name=screen_name).AsDict()
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
        tweets = [tweet.AsDict() for tweet in tweets]
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
        user_lists = [ulist.AsDict() for ulist in user_lists]
        make_cache(user_lists, user_id, 'list', 'jsonlist')

    return user_lists


def get_user_data(api, screen_name=None, user_id=None, ctr=0):

    try:

        target = get_user_info(api, screen_name=screen_name, user_id=user_id)
        tweets = get_user_tweets(api, user_id=target['id'])
        followers = get_user_followers(api, user_id=target['id'])
        following = get_user_following(api, user_id=target['id'])
        user_lists = get_user_lists(api, user_id=target['id'])
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


def get_follower_data(apis, followers):
    '''
    apis:
    followers:
    return:
    '''
    num_apis = len(apis)

    for ind, id in enumerate(followers):

        print ind, id

        n = ind % num_apis

        user_data = get_user_data(apis[n], user_id=id)

        if user_data:
            user, tweets, fol_followers, fol_following, fol_lists = user_data
        else:
            continue

        #if n == 0 and ind > 4550:
        #    print 'sleep for 30 at', ind
        #    time.sleep(60*ind/10000)

        ## PARSE THIS DATA, RETURN USABLE INFORMATION BACK AS DATAFRAME

    return None