# -*- coding: utf-8 -*-
import pandas as pd

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


def parse_user_info(info, src=''):
    if src in info:
        return info[src]
    return ''


def parse_user_tweets(tweets, src='', sub=None, sub_cond=None, cond=None):
    if not type(tweets) == list: return []
    result = set()
    for tweet in tweets:
        d = tweet if src in tweet else __flatten(tweet)

        if sub != None and sub_cond != None and src in d:
            for x in d[src]:
                if d[sub_cond] == cond:
                    result.add(x[sub])

        elif sub != None and src in d:
            for x in d[src]:
                result.add(x[sub])

        elif src in d:
            if sub_cond != None:
                if d[sub_cond] == cond and type(d[src]) == list:
                    for x in d[src]:
                        result.add(x)
                elif d[sub_cond] == cond and type(d[src]) != list:
                    result.add(d[src])

            else:
                if type(d[src]) == list:
                    for x in d[src]:
                        result.add(x)

    return result


def parse_user_followers(followers):
    return set(followers)


def parse_user_following(following):
    return set(following)


def parse_user_lists(user_list):
    if not type(user_list) == list: return set()
    return set([ul['id'] for ul in user_list])


def parse_dataframe(in_df):

    df = pd.DataFrame()
    df['id'] = in_df.index
    df = df.set_index('id')

    df['screen_name'] = in_df['info'].apply(parse_user_info, src='screen_name')
    df['name'] = in_df['info'].apply(parse_user_info, src='name')
    df['location'] = in_df['info'].apply(parse_user_info, src='location')

    df['tweets'] = in_df['tweets'].apply(parse_user_tweets,
                                        src='text', sub_cond='lang', cond='en')

    df['mentions'] = in_df['tweets'].apply(parse_user_tweets,
                                           src='user_mentions', sub='id')

    df['hashtags'] = in_df['tweets'].apply(parse_user_tweets, src='hashtags')

    df['urls'] = in_df['tweets'].apply(parse_user_tweets, src='urls', sub=0)

    df['followers'] = in_df['followers'].apply(parse_user_followers)
    df['following'] = in_df['following'].apply(parse_user_following)
    df['list'] = in_df['list'].apply(parse_user_lists)

    return df


def filter_dataframe(in_df, min_followers=1, min_following=1, min_tweets=0):
    df = in_df.copy()
    df = df[df['followers'].apply(len) >= min_followers]
    df = df[df['following'].apply(len) >= min_following]
    df = df[df['tweets'].apply(len) >= min_tweets]
    return df