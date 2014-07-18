# -*- coding: utf-8 -*-

def get_cache(db, user_id, cache_type):
    '''
    user_id:
    cache_type:

    return:
    '''
    coll = db.data

    tmp = coll.find_one({'id': user_id, 'type': cache_type})

    if tmp:
        return tmp['data']
    else:
        return None


def make_cache(db, data, user_id, cache_type):
    '''
    data:
    user_id:
    cache_type:

    return: None
    '''

    coll = db.data

    # The update+upsert does two things:
    #  - If a document for user_id-cache_type is found, the 'data' field is
    #    updated with the data passed into the function.
    #  - If a document for user-id-cache_type is not found, a new document is
    #    created with the id, type, and data fields.
    coll.update({'id': user_id, 'type': cache_type},
                {'$set': {'data': data}},
                upsert = True)