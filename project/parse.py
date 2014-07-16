# -*- coding: utf-8 -*-
import pandas as pd


def parse_user_info(info):
    pass


def parse_user_tweets(tweets):
    pass
    #res = []
    #for tweet in tweets:



def parse_user_followers(followers):
    pass


def parse_user_following(following):
    pass


def parse_user_lists(lists):
    pass


def parse_user_data(user_data):

    if not user_data: return None

    user, tweets, fol_followers, fol_following, fol_lists = user_data

    return user_dict