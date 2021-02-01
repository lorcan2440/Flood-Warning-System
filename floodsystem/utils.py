# Copyright (C) 2018 Garth N. Wells
#
# SPDX-License-Identifier: MIT

'''
This module contains utility functions.
'''


def sorted_by_key(x, i, reverse=False):

    '''
    For a list of lists/tuples, return list sorted by the ith
    component of the list/tuple, e.g.

    Sort on second entry of tuple:

      > sorted_by_key([(1, 2), (5, 1]), 1)
      >>> [(5, 1), (1, 2)]
    '''

    # Sort by distance
    def key(element):
        return element[i]

    return sorted(x, key=key, reverse=reverse)


def wgs84_to_web_mercator(coord: tuple):

    '''
    Returns a tuple of web mercator (x, y) coordinates
    compatible with the Bokeh plotting module given a tuple of
    (long, lat) coords.
    https://en.wikipedia.org/wiki/Web_Mercator_projection
    '''
    import math

    lat, lon = coord[0], coord[1]
    R_MAJOR = 6378137.000
    x = R_MAJOR * math.radians(lon)
    scale = x / lon
    y = 180.0 / math.pi * math.log(math.tan(math.pi / 4.0 + lat * (math.pi / 180.0) / 2.0)) * scale

    return (x, y)
