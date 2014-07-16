# -*- coding: utf-8 -*-
import twitter
import os

def oauth_login(api_key_file):
    '''
    Login to twitter using oauth login credentials stored in a file.

    api_key_file: File object or path to directory/file Object as String

    return: twitter.Api object oauth login
    '''

    if type(api_key_file) == str:
        if os.path.isfile(api_key_file):
            api_file = [open(api_key_file, 'r')]
        else:
            api_file = [open(os.path.join(api_key_file, fn), 'r')
                            for fn in next(os.walk(api_key_file))[2]]
    else:
        api_file = [api_key_file]

    apis = []
    for fn in api_file:
        api_key, api_pass, tok_key, tok_pass = [str(x).strip() for x in fn]
        api = twitter.Api(consumer_key = api_key,
                          consumer_secret = api_pass,
                          access_token_key = tok_key,
                          access_token_secret = tok_pass,
                          use_gzip_compression = True)
        apis.append(api)

    if len(apis) == 1:
        return apis[0]

    return apis