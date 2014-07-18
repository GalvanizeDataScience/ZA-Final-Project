# -*- coding: utf-8 -*-
import numpy as np

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

    shared_list = user1['lists'].intersection(user2['lists'])
    shared_hashtags = user1['hashtags'].intersection(user2['hashtags'])
    shared_mentions = user1['mentions'].intersection(user2['mentions'])
    shared_urls = user1['urls'].intersection(user2['urls'])

    similarity  = FOLLOWING_EACH_OTHER_WEIGHT * (user1_follow_user2 and user1_follow_user2)
    similarity += FOLLOWING_ONE_WAY_WEIGHT * (user1_follow_user2 ^ user2_follow_user1)
    similarity += MENTION_OTHER_USER_WEIGHT * user1_mention_user2
    similarity += MENTION_OTHER_USER_WEIGHT * user2_mention_user1
    similarity += SHARED_FOLLOWERS_WEIGHT * len(shared_followers)
    similarity += SHARED_FOLLOWING_WEIGHT * len(shared_following)
    similarity += SHARED_LIST_WEIGHT * len(shared_list)
    similarity += SHARED_MENTION_WEIGHT * len(shared_mentions)
    similarity += SHARED_HASHTAG_WEIGHT * len(shared_hashtags)
    similarity += SHARED_URLS_WEIGHT * len(shared_urls)

    return similarity


def build_attributes(user_df):
    result = {}
    for user_id in user_df.index:

        result[user_id] = {}
        user = user_df.ix[user_id,:]

        if type(user['followers']) != set:
            result[user_id]['followers'] = set(user['followers'])
        else:
            result[user_id]['followers'] = user['followers']

        if type(user['following']) != set:
            result[user_id]['following'] = set(user['following'])
        else:
            result[user_id]['following'] = user['followers']

        result[user_id]['lists'] = set([x['id'] for x in user['lists']])

        user_hashtags = set()
        user_mentions = set()
        user_urls = set()

        for tweet in user['tweets']:
            if 'user_mentions' in tweet:
                for uid in tweet['user_mentions']:
                    user_mentions.add(uid)
            if 'urls' in tweet:
                for url in tweet['urls']:
                    user_urls.add(url[0])
            if 'hashtags' in tweet:
                for hashtag in tweet['hashtags']:
                    user_hashtags.add(hashtag)

        result[user_id]['hashtags'] = user_hashtags
        result[user_id]['mentions'] = user_mentions
        result[user_id]['urls'] = user_urls

    return result


def build_similarity_matrix(user_df):

    similarity_matrix = np.zeros([user_df.shape[0]]*2)

    attribute_dict = build_attributes(user_df)
    print 'finished building similarity matrix'

    for i, user1_id in enumerate(user_df.index[:-1]):

        for j, user2_id in enumerate(user_df.index[i+1:]):
            similarity = compute_similarity(user1_id, attribute_dict[user1_id],
                                            user2_id, attribute_dict[user2_id])

            similarity_matrix[i, j] = similarity
            similarity_matrix[j, i] = similarity

    return similarity_matrix
