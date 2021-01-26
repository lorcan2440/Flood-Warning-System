# Copyright (C) 2018 Garth N. Wells
#
# SPDX-License-Identifier: MIT

"""
This module contains a collection of functions related to
geographical data.
"""

from .utils import sorted_by_key
from .haversine import haversine, Unit
from .station import MonitoringStation


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


def stations_within_radius(stations: list, centre: tuple, r: float):

    '''
    Returns a list of all stations (type MonitoringStation)
    within radius r of a geographic coordinate x.
    '''

    assert all([isinstance(i, MonitoringStation) for i in stations])
    assert type(centre) == tuple
    assert type(r) == float or type(r) == int

    stations_in_range = []

    for station in stations:
        if haversine(station.coord, centre, unit=Unit.KILOMETERS) <= r:
            stations_in_range.append(station.name)

    return sorted(stations_in_range)


def rivers_with_station(stations: list):

    '''
    Returns a set of the names of all rivers which have
    a MonitoringStation instance associated with them.
    '''

    assert all([isinstance(i, MonitoringStation) for i in stations])

    rivers = {station.river.strip() for station in stations}

    return rivers


def stations_by_river(stations: list):

    '''
    Returns a dict that maps river names to a list of
    station objects associated with that river.
    '''

    rivers = rivers_with_station(stations)

    river_dict = {}
    for river in rivers:
        pair = {river: [station for station in stations if station.river == river]}
        river_dict.update(pair)

    return river_dict


def rivers_by_station_number(stations: list, N: int):

    '''
    Returns a list of (river name, number of stations)
    tuples. The tuples are sorted by number of stations,
    and only the top N values are included. Where several
    rivers have the same number of stations, all such
    rivers are included in the list.
    '''

    river_names = rivers_with_station(stations)
    river_dict = stations_by_river(stations)

    river_num_list = sorted([(r, len(river_dict[r])) for r in river_names],
                            key=lambda x: x[1], reverse=True)

    end_num = sorted(list({r[1] for r in river_num_list}), reverse=True)[N - 1]

    rivers_list = []
    for (r, n) in river_num_list:
        if n >= end_num:
            rivers_list.append((r, n))
        else:
            break

    return rivers_list
