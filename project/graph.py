# -*- coding: utf-8 -*-
import networkx as nx
import community


def make_edges(source, target, weights=None):
    '''
    source: String/Integer or List of source
    target: String/Integer or List of target
    weights: List of Integer/Floats. Must be the same size as either the
    target or source

    return: List of [source, target, weight] objects
    '''

    source = source if type(source) == list else [source]
    target = target if type(target) == list else [target]

    if len(source) != len(target):
        if len(source) > len(target) and len(target) == 1:
            target *= len(source)

        elif len(source) < len(target) and len(source) == 1:
            source *= len(target)

    return [(x,y,float(z)) for x,y,z in zip(source,target,weights)]


def make_verts(source_id, attrs = None):
    '''
    :param source_id:
    :param attrs:
    :return:
    '''


def make_partitions(g, optimize=True):

    p0 = community.best_partition(g)

    if not optimize:
        return p0

    p1 = community.best_partition(g, partition=p0)

    while p0 != p1:
        p0 = community.best_partition(g, partition=p1)
        p1 = community.best_partition(g, partition=p0)

    return [[k for k in p1.keys() if p1[k] == v] for v in set(p1.values())]


def make_graph(df, partitions=False, optimize=False):

    edges = make_graph(target['id'], followers, apis)

    g = nx.Graph(data=edges)

    if partitions:
        return g, make_partitions(g, optimize=optimize)

    return g


