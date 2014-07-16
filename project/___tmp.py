# -*- coding: utf-8 -*-
import os
import pymongo
from cache import get_cache

def traverse_dict(d):
    for k, v in d.iteritems():
        if k in ('url', 'urls') and type(v) == dict:
            d[k] = d[k].keys()
        elif type(v) == dict:
            d[k] = traverse_dict(v)
    return d


def store_in_mongo():
    BASE  = '../cache/'
    FILES = [os.path.join(BASE,fn) for fn in next(os.walk(BASE))[2]]

    conn = pymongo.MongoClient("localhost", 27017)
    db   = conn.twitter
    coll = db.data

    for f in FILES:

        fn = f.split('/')[2]

        if fn[0] == '.': continue

        uid, types = fn.split('_')
        uid = int(uid)
        ctype, ftype = types.split('.')

        print uid, ctype, ftype

        data = get_cache(uid, ctype, ftype)

        if ctype == 'tweets':
            for i in range(len(data)):
                data[i] = traverse_dict(data[i])

        if ctype in ('info'):
            data = traverse_dict(data)

        coll.insert({'id': uid, 'type': ctype, 'data': data})
