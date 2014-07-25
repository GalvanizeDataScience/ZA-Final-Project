# -*- coding: utf-8 -*-
from copy import deepcopy
from data import get_user_data_by_type

def convert_id_to_sn(user_id, df, db, api):

    if user_id in df.index:
        return df.ix[user_id, 'screen_name']

    info = get_user_data_by_type(db, api, user_id = user_id, data_type='info')

    return info['screen_name']

def get_screen_names(data_in, target, df, db, api):

    d = deepcopy(data_in)

    for lvl in d:

        for cid in d[lvl]:

            for i, tag in enumerate(d[lvl][cid][target]):

                sn = convert_id_to_sn(tag, df, db, api)

                if sn == None:
                    d[lvl][cid][target][i] = '@<Protected_User>'

                else:
                    d[lvl][cid][target][i] = '@' + sn

    return d