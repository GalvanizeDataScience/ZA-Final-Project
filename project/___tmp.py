# -*- coding: utf-8 -*-
import os
import pymongo
from cache import get_cache

URLS = ('url', 'urls')

def __traverse(in_dict, lookup):
    d = in_dict.copy()
    for k, v in d.iteritems():
        if k in lookup and type(v) == dict:
            d[k] = d[k].items()
        elif type(v) == dict:
            d[k] = __traverse(v, lookup)
    return d


def store_in_mongo():
    BASE  = '../cache/'
    FILES = [os.path.join(BASE,fn) for fn in next(os.walk(BASE))[2]]

    conn = pymongo.MongoClient("localhost", 27017)
    db   = conn.twitter
    coll = db.data

    for f in FILES:
        print f
        fn = f.split('/')[2]

        if fn[0] == '.': continue

        uid, types = fn.split('_')
        uid = int(uid)
        ctype, ftype = types.split('.')

        print uid, ctype, ftype

        data = get_cache(uid, ctype, ftype)

        if ctype == 'tweets':
            for i in range(len(data)):
                data[i] = __traverse(data[i], URLS)

        if ctype in ('info'):
            data = __traverse(data, URLS)

        coll.insert({'id': uid, 'type': ctype, 'data': data})

if __name__ == '__main__':
    store_in_mongo()