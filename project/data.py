# -*- coding: utf-8 -*-
import pandas as pd
import twitter
import time

URLS = ('url', 'urls')
FOLLOWERS_CAP = 50000
FOLLOWING_CAP = 50000

API_CALLS = {'list': 'GetListsList',
             'following': 'GetFriendIDs',
             'followers':'GetFollowerIDs',
             'tweets': 'GetUserTimeline',
             'info': 'GetUser',
             }

API_ARGS = {'list': {},
            'following': {},
            'followers': {},
            'tweets': {'count': 200, 'trim_user': True},
            'info': {},
            }


def __traverse(in_dict, lookup):

    d = in_dict.copy()

    for k, v in d.iteritems():

        if k in lookup and type(v) == dict:
            d[k] = d[k].items()

        elif type(v) == dict:
            d[k] = __traverse(v, lookup)

    return d


def __get_cache(db, followers):

    result = {}

    curs = db.data.find({'id': {'$in': followers}})

    for data in curs:

        uid = data['id']

        dtype = data['type']

        if uid not in result:
            result[uid] = {}

        result[uid][dtype] = data['data']

    curs.close()

    return result


def __get_cache_for_user(db, user_id, cache_type):

    if user_id:
        coll = db.data
        tmp = coll.find_one({'id': user_id, 'type': cache_type})
        if tmp:
            return tmp['data']
    return None


def __make_cache_for_user(db, data, user_id, cache_type):

    coll = db.data
    coll.update({'id': user_id, 'type': cache_type},
                {'$set': {'data': data}},
                upsert = True)


def get_user_data_by_type(db, api, screen_name=None,
                          user_id=None, data_type=None, force=False):

    if force:
        data = None
    else:
        data = __get_cache_for_user(db, user_id, data_type)

    if data == None:

        data = eval('api.' + API_CALLS[data_type] + \
                    '(screen_name=screen_name, user_id=user_id, ' + \
                    '**API_ARGS[data_type])')

        if data_type == 'list':
            data = [__traverse(x.AsDict(), URLS) for x in data]

        elif data_type == 'tweets':
            data = [__traverse(x.AsDict(), URLS) for x in data]

        elif data_type == 'info':
            data = __traverse(data.AsDict(), URLS)

        __make_cache_for_user(db, data, user_id, data_type)

    return data


def get_user_data(db, api, name=None, uid=None, ctr=0, force=False):

    try:
        target = get_user_data_by_type(db, api, screen_name=name,
                                       user_id=uid, data_type='info',
                                       force=force)

        if 'followers_count' in target:
            if target['followers_count'] > FOLLOWERS_CAP:
                return None

        if 'friends_count' in target:
            if target['friends_count'] > FOLLOWING_CAP:
                return None

        tweets = get_user_data_by_type(db, api, user_id=target['id'],
                                       data_type='tweets', force=force)

        user_lists = get_user_data_by_type(db, api, user_id=target['id'],
                                           data_type='list', force=force)

        followers = get_user_data_by_type(db, api, user_id=target['id'],
                                          data_type='followers', force=force)

        following = get_user_data_by_type(db, api, user_id=target['id'],
                                          data_type='following', force=force)

        return target, tweets, followers, following, user_lists

    except (twitter.error.TwitterError, twitter.TwitterError) as err:

        if str(err)[0:3] == 'Not' or ctr > 15:
            print 'User is protected:', uid

        elif '63' in str(err):
            print 'User has been suspended:', uid

        elif '88' in str(err):
            print 'Rate Limit reached on:', uid
            time.sleep(60)
            return get_user_data(db, api, name = name, uid = uid, ctr = ctr+1)

        else:
            print err

        return None


def get_follower_data(db, apis, followers, force=False):

    num_apis = len(apis)

    num_followers = len(followers)

    # Begin by doing a mass-check for cached data
    if force:
        result = {}
    else:
        result = __get_cache(db, followers)

    for ind, uid in enumerate(followers):

        if uid in result:
            if len(result[uid].keys()) == 5:
                continue

        print ind + 1, 'of', num_followers, '. On id:', uid

        n = ind % num_apis

        user_data = get_user_data(db, apis[n], uid=uid, force=force)

        result[uid] = user_data

    # transpose so that user_id are rows and columns are the fields
    # dropna() will remove users that had protected or overly large
    # follower/friends lists. It will NOT remove users width no tweets / no
    # lists
    return pd.DataFrame(data=result).transpose().dropna()
