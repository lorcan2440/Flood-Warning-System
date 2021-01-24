# Copyright (C) 2018 Garth N. Wells
#
# SPDX-License-Identifier: MIT

"""
This module contains a collection of functions related to
geographical data.
"""

from .utils import sorted_by_key
from .haversine import haversine, Unit


def stations_by_distance(stations: list, p: tuple):

    '''
    Returns a list of (station, distance) tuples, where
    station is a MonitoringStation object and distance
    is the float distance of that station from the given
    coordinate p.
    '''

    assert type(stations) == list
    assert type(p) == tuple

    my_data = []
    for s in stations:
        # Try adding the (station, distance) tuple
        try:
            my_data.append((s, haversine(s.coord, p, unit=Unit.KILOMETERS)))
        # If the coord attribute of a station is missing,
        # the haversine function will throw ValueError,
        # so skip this station
        except ValueError:
            pass

    sorted_data = sorted_by_key(my_data, 1)

    return sorted_data
