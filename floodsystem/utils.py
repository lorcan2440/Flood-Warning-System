# Copyright (C) 2018 Garth N. Wells
#
# SPDX-License-Identifier: MIT

'''
This module contains utility functions.
'''

import numpy as np


def sorted_by_key(nested_list: list[tuple], index: int, reverse: bool = False) -> list[tuple]:

    '''
    For a list of lists/tuples, return list sorted by the ith
    component of the list/tuple.
    '''

    return sorted(nested_list, key=lambda x: x[index], reverse=reverse)


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


def wgs84_to_web_mercator_vector(coords: np.ndarray) -> np.ndarray:

    '''
    Returns an array of (x, y) coords corresponding to a given array of (lat, long) coords.
    '''

    if any(not (-90 < coord[0] < 90 and -180 <= coord[1] <= 180) for coord in coords):
        raise ValueError('Latitude must be between -90 and 90, and Longitude must be between -180 and 180.')

    if not isinstance(coords, np.ndarray):
        coords = np.array(coords)

    lats, longs = coords[:, 0], coords[:, 1]

    R_MAJOR = 6378137.000  # (major) radius of earth in m
    x = R_MAJOR * np.radians(longs)
    y = np.nan_to_num(np.degrees(np.log(np.tan(np.pi / 4 + 0.5 * np.radians(lats))) * (x / longs)),
        nan=np.log(np.tan(np.pi / 4 + 0.5 * np.radians(lats))) * R_MAJOR)

    return np.transpose((x, y))


def flatten(t: list[list]) -> list:

    '''
    Given a list of lists, returns a single list containing all
    the elements of each list in the original list. Also works
    with tuples (but not sets or dicts)
    '''

    return [item for sublist in t for item in sublist]


def coord_letters(lat: float, long: float) -> tuple[str, str]:

    '''
    Determines whether a coordinate is in the North/South and East/West hemispheres
    and assigns them a corresponding letter.

    The Equator is considered North and the Prime Meridian is considered East.
    '''

    return ('N' if lat >= 0 else 'S', 'E' if long >= 0 else 'W')


def get_else_none(var, index=None, func: callable = lambda x: x):

    '''
    Gets an item from a dict or list, unless the dict itself is None,
    in which case returns None.
    '''

    if var is not None:
        if index is not None:
            if isinstance(var, dict):
                tmp = var.get(index, None)
                return func(tmp) if tmp is not None else None
            elif isinstance(var, (list, tuple)) and 0 <= index < len(var):
                return func(var[index])
            else:
                return None
        else:
            return func(var)
    else:
        return None

