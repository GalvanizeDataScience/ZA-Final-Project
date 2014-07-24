# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd

FOLLOWING_EACH_OTHER_WEIGHT = 10.
FOLLOWING_ONE_WAY_WEIGHT = 5.

SHARED_FOLLOWERS_WEIGHT = 1.
SHARED_FOLLOWING_WEIGHT = 1.

SHARED_LIST_WEIGHT = 1.
SHARED_MENTION_WEIGHT = 1.
SHARED_HASHTAG_WEIGHT = 1.
SHARED_URLS_WEIGHT = 1.

MENTION_OTHER_USER_WEIGHT = 10.


def compute_similarity(user1_id, user1, user2_id, user2):

    user1_follow_user2 = user2_id in user1['following']
    user2_follow_user1 = user2_id in user1['followers']

    user1_mention_user2 = user2_id in user1['mentions']
    user2_mention_user1 = user1_id in user2['mentions']

    shared_followers = user1['followers'].intersection(user2['followers'])
    shared_following = user1['following'].intersection(user2['following'])

    shared_list = user1['list'].intersection(user2['list'])
    shared_hashtags = user1['hashtags'].intersection(user2['hashtags'])
    shared_mentions = user1['mentions'].intersection(user2['mentions'])
    shared_urls = user1['urls'].intersection(user2['urls'])

    similarity  = FOLLOWING_EACH_OTHER_WEIGHT * \
                  (user1_follow_user2 and user1_follow_user2)
    similarity += FOLLOWING_ONE_WAY_WEIGHT * \
                  (user1_follow_user2 ^ user2_follow_user1)
    similarity += MENTION_OTHER_USER_WEIGHT * user1_mention_user2
    similarity += MENTION_OTHER_USER_WEIGHT * user2_mention_user1
    similarity += SHARED_FOLLOWERS_WEIGHT * len(shared_followers)
    similarity += SHARED_FOLLOWING_WEIGHT * (len(shared_following) - 1)
    similarity += SHARED_LIST_WEIGHT * len(shared_list)
    similarity += SHARED_MENTION_WEIGHT * len(shared_mentions)
    similarity += SHARED_HASHTAG_WEIGHT * len(shared_hashtags)
    similarity += SHARED_URLS_WEIGHT * len(shared_urls)

    return similarity


def make_similarity_dataframe(df):
    similarity_df = pd.DataFrame(data=np.zeros([df.shape[0]]*2),
                                 index=df.index, columns=df.index)
    for i, user1_id in enumerate(df.index[:-1]):
        for user2_id in df.index[i+1:]:
            similarity = compute_similarity(user1_id, df.ix[user1_id, :],
                                            user2_id, df.ix[user2_id, :])
            similarity_df.ix[user1_id, user2_id] = similarity
            similarity_df.ix[user2_id, user1_id] = similarity

    return similarity_df
