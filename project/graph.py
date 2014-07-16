# -*- coding: utf-8 -*-
import graphlab
from graphlab import Vertex
from graphlab import Edge


def make_edges(source, target, weight=None):
    '''
    source: String/Integer or List of source
    target: String/Integer or List of target

    return: List of Edge(source, target) objects
    '''

    source = source if type(source) == list else [source]
    target = target if type(target) == list else [target]

    if len(source) != len(target):
        if len(source) > len(target) and len(target) == 1:
            target *= len(source)

        elif len(source) < len(target) and len(source) == 1:
            source *= len(target)

    #return [Edge(int(x),int(y)) for x,y in zip(source, target)]
    return [(int(x), int(y)) for x, y in zip(source, target)]


def make_verts(source_id, attrs = None):
    '''
    :param source_id:
    :param attrs:
    :return:
    '''

    if not attrs:
        return Vertex(source_id)

    else:
        return Vertex(source_id, attr=attrs)


def make_graph(target_id, followers, apis, update=False):

    #cache_path = '../cache/_graphs/'
    #file_name  = str(target_id) + '.graph'

    #if os.path.isfile(cache_path + file_name) and not update:
    #   return gl.load_graph(cache_path + file_name)

    g - graphlab.SGraph()

    verts = [make_verts(target_id)]

    edges = make_edges(followers, target_id)

    verts.append(make_verts(id))

    #if fol_followers: edges.extend(make_edges(fol_followers, id))

    #if fol_following: edges.extend(make_edges(id, fol_following))


    #g = gl.SGraph().add_vertices(verts).add_edges(edges)

    #g.save(cache_path + file_name)

    return g