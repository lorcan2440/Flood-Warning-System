# Copyright (C) 2018 Garth N. Wells
#
# SPDX-License-Identifier: MIT

'''
This module contains utility functions.
'''


def sorted_by_key(x: list[tuple], i: int, reverse: bool = False) -> list[tuple]:

    '''
    For a list of lists/tuples, return list sorted by the ith
    component of the list/tuple, e.g.

    Sort on second entry of tuple:

      > sorted_by_key([(1, 2), (5, 1]), 1)
      >>> [(5, 1), (1, 2)]
    '''

    return sorted(x, key=lambda x: x[i], reverse=reverse)


def wgs84_to_web_mercator(coord: tuple) -> tuple:

    '''
    Returns a tuple of web mercator (x, y) coordinates
    compatible with the Bokeh plotting module given a tuple of
    (long, lat) coords.
    https://en.wikipedia.org/wiki/Web_Mercator_projection
    '''

    import math

    lat, lon = coord
    R_MAJOR = 6378137.000
    x = R_MAJOR * math.radians(lon)
    scale = x / lon
    y = 180.0 / math.pi * math.log(math.tan(math.pi / 4.0 + lat * (math.pi / 180.0) / 2.0)) * scale

    return (x, y)


def flatten(t: list[list]) -> list:

    '''
    Given a list of lists, returns a single list containing all
    the elements of each list in the original list. Also works
    with tuples (but not sets or dicts)
    '''

    return [item for sublist in t for item in sublist]
