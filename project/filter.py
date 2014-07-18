# -*- coding: utf-8 -*-

def filter_user_dataframe(user_df,
                          min_followers=1, min_following=1, min_tweets=0):
    '''
    user_df: dataframe
    min_followers:
    min_following:
    min_tweets:
    return: dataframe
    '''

    df = user_df.copy()
    df = df[df['followers'].apply(len) >= min_followers]
    df = df[df['following'].apply(len) >= min_following]
    df = df[df['tweets'].apply(len) >= min_tweets]
    return df