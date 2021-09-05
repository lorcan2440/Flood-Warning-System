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


def wgs84_to_web_mercator(coord: tuple[float]) -> tuple[float]:

    '''
    Returns a tuple of web mercator (x, y) coordinates compatible with the
    Bokeh plotting module given a tuple of (lat, long) coords.
    https://en.wikipedia.org/wiki/Web_Mercator_projection

    Actual support for google maps is latitude between -85.06 and 85.06.
    '''

    from math import pi, log, tan, radians, degrees

    if not bool(-90 < coord[0] < 90 and -180 <= coord[1] <= 180):
        raise ValueError('Latitude must be between -90 and 90, and Longitude must be between -180 and 180.')
    lat, long = coord[0], coord[1]
    R_MAJOR = 6378137.000  # (major) radius of earth in m
    x = R_MAJOR * radians(long)
    if long != 0:
        y = degrees(log(tan(pi / 4 + 0.5 * radians(lat))) * (x / long))
    else:
        y = log(tan(pi / 4 + 0.5 * radians(lat))) * R_MAJOR
    return (x, y)


def flatten(t: list[list]) -> list:

    '''
    Given a list of lists, returns a single list containing all
    the elements of each list in the original list. Also works
    with tuples (but not sets or dicts)
    '''

    return [item for sublist in t for item in sublist]
