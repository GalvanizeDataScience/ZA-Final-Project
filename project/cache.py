# -*- coding: utf-8 -*-
import os
import json

BASE_ADDRESS = '../cache/'

def get_cache(user_id, cache_type, file_type):
    '''
    user_id:
    cache_type:
    file_type:

    return:
    '''

    file_name = str(user_id) + '_' + cache_type + '.' + file_type

    if not os.path.isfile(BASE_ADDRESS + file_name):
        return None

    with open(BASE_ADDRESS + file_name, 'rb') as fh:
        if file_type == 'csv':
            try:
                data = map(int, fh.read().strip().split(','))
            except ValueError:
                data = []

        elif file_type == 'json':
            try:
                data = json.loads(fh.read().strip())
            except ValueError:
                data = {}

        elif file_type == 'jsonlist':
            try:
                data = [json.loads(row.strip()) for row in fh]
            except ValueError:
                data = []

        else:
            data = str(fh.read().strip())

    return data


def make_cache(data, user_id, cache_type, file_type):
    '''
    data:
    user_id:
    cache_type:
    file_type:

    return:
    '''
    if file_type == 'csv':
        to_write = ','.join(map(str, data))

    elif file_type == 'json':
        to_write = json.dumps(data)

    elif file_type == 'jsonlist':
        to_write = '\n'.join([json.dumps(row) for row in data])

    else:
        to_write = str(data)

    file_name = str(user_id) + '_' + cache_type + '.' + file_type

    with open(BASE_ADDRESS + file_name, 'wb') as fh:
        fh.write(to_write)