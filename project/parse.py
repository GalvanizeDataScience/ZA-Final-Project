# -*- coding: utf-8 -*-

# Source: http://stackoverflow.com/posts/6027703/revisions
def __flatten(d, lkey=''):
    ret = {}
    for rkey,val in d.items():
        key = lkey + rkey
        if isinstance(val, dict):
            ret.update( __flatten(val, key + '_') )
        else:
            ret[key] = val
    return ret


def parse_user_info(info):

    TO_KEEP = {'followers_count', 'friends_count', 'lang', 'name','protected',
               'screen_name','location', 'status_user_mentions',
               'status_urls', 'status_hashtags'}

    d = __flatten(info.copy())
    for k in d.keys():
        if k not in TO_KEEP: del d[k]
    if 'status_user_mentions' in d:
        d['status_user_mentions'] = [x['id'] for x in d['status_user_mentions']]

    return d


def parse_user_tweets(tweets):

    if not type(tweets) == list: return tweets

    TO_KEEP = {'text', 'geo_coordinates', 'place_bounding_box_coordinates',
               'place_id', 'user_mentions', 'hashtags', 'urls'}

    result = []
    for tweet in tweets:
        d = __flatten(tweet.copy())
        for k in d.keys():
            if k not in TO_KEEP: del d[k]
        if 'user_mentions' in d:
            d['user_mentions'] = [x['id'] for x in d['user_mentions']]
        result.append(d)
    return result

def parse_user_followers(followers):
    return set(followers)


def parse_user_following(following):
    return set(following)


def parse_user_lists(lists):
    if not type(lists) == list:
        return lists
    elif len(lists) == 0:
        return lists

    TO_KEEP = {'id', 'name', 'member_count', 'subscriber_count',
               'user_id', 'user_url'}

    result = []
    for ul in lists:
        d = __flatten(ul.copy())
        for k in d.keys():
            if k not in TO_KEEP: del d[k]
        result.append(d)
    return result


def parse_user_data(user_data, parse_data=True):

    if not user_data: return None

    uinfo, utweets, ufollowers, ufollowing, ulists = user_data

    if parse_data:
        return {'info': parse_user_info(uinfo),
                'tweets': parse_user_tweets(utweets),
                'followers': parse_user_followers(ufollowers),
                'following': parse_user_following(ufollowing),
                'lists': parse_user_lists(ulists)}

    return {'info': uinfo,
            'tweets': utweets,
            'followers': ufollowers,
            'following': ufollowing,
            'lists': ulists}