# -*- coding: utf-8 -*-
from copy import deepcopy
from data import get_user_data_by_type

def convert_id_to_sn(user_id, df, db, api):

    if user_id in df.index:
        return df.ix[user_id, 'screen_name']

    info = get_user_data_by_type(db, api, user_id = user_id, data_type='info')

    return info['screen_name']

def get_screen_names(dict_of_ids, df, db, api):

    d = deepcopy(dict_of_ids)

    for k0,v0 in dict_of_ids.items():

        for k1, v1 in v0.items():

            for i, tag in enumerate(v1):

                sn = convert_id_to_sn(d[k0][k1][i], df, db, api)

                if sn == None:
                    d[k0][k1][i] = '@<Protected_User>'

                else:
                    d[k0][k1][i] = '@' + sn

    return d