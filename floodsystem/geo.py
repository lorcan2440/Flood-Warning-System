'''
This module contains a collection of functions related to
geographical data.
'''

# pylint: disable=relative-beyond-top-level, no-name-in-module

from .utils import sorted_by_key, haversine_vector, Unit
from .station import MonitoringStation


def stations_by_distance(stations: list, p: tuple) -> list[tuple[MonitoringStation, float]]:

    '''
    Returns a list of (station, distance) tuples, where station is a `MonitoringStation`
    and distance is the float distance of that station from the given coordinate p.
    '''

    # Standard data type input checks
    assert isinstance(stations, list) and all([isinstance(i, MonitoringStation) for i in stations])
    assert isinstance(p, tuple)

    # preserve original order in case of other scripts running at the same time
    _stations = stations
    ref_points, station_points = [p for i in range(len(_stations))], [s.coord for s in _stations]

    # use haversine_vector to efficiently find the distance between multiple points
    my_data = zip(_stations, list(haversine_vector(ref_points, station_points, unit=Unit.KILOMETERS)))
    del _stations

    # sort by distance (second item in each list)
    return sorted_by_key(my_data, 1)


def stations_within_radius(stations: list, centre: tuple, r: float) -> list[MonitoringStation]:

    '''
    Returns a list of all stations (type MonitoringStation)
    within radius r of a geographic coordinate centre.
    '''

    # standard data type input checks
    assert isinstance(r, (float, int))

    # get all (station, distance) pairs
    sorted_stations = stations_by_distance(stations, centre)

    # return station where distance is <= the given radius
    return [s[0] for s in sorted_stations if s[1] <= r]


def rivers_with_station(stations: list) -> set[str]:

    '''
    Returns a set of the names of all rivers which have
    a MonitoringStation instance associated with them.
    '''

    # Standard data type input checks
    assert all([isinstance(i, MonitoringStation) for i in stations])

    # Set (comprehension) to skip over/remove duplicates
    rivers = {getattr(s, 'river', None) for s in stations} - {None}

    return rivers


def stations_by_river(stations: list) -> dict[str: list[MonitoringStation]]:

    '''
    Returns a dict that maps river names to a list of
    station objects associated with that river.
    '''

    # Standard data type input checks
    assert all([isinstance(i, MonitoringStation) for i in stations])

    rivers = rivers_with_station(stations)

    # For each river listed, add all its associated stations.
    river_dict = {river: list(filter(lambda s: getattr(s, 'river', None) == river, stations))
        for river in rivers}

    return river_dict


def rivers_by_station_number(stations: list, n: int) -> list[tuple[str, int]]:

    '''
    Returns a list of (river name, number of stations)
    tuples. The tuples are sorted by number of stations,
    and only the top N values are included. Where several
    rivers have the same number of stations, all such
    rivers are included in the list.
    '''

    # Standard data type input and bounds checks
    assert all([isinstance(i, MonitoringStation) for i in stations])
    assert isinstance(n, int)
    assert n >= 1

    river_names = rivers_with_station(stations)
    river_dict = stations_by_river(stations)

    # Get a complete list of (river name, number of stations) tuples, sorted descending
    river_num_list = sorted_by_key([(r, len(river_dict[r])) for r in river_names], 1, reverse=True)

    # Find the number of stations which is N from the highest, accounting for possible duplicates
    end_num = sorted(list({r[1] for r in river_num_list}), reverse=True)[n - 1]

    # Create list of (river name, number of stations) tuples up to the found limit
    return [(r, n) for r, n in river_num_list if r is not None and n >= end_num]


def stations_by_town(stations: list) -> dict[str: list[MonitoringStation]]:

    '''
    Returns a dict that maps town names to a list of
    station objects associated with that town.
    '''

    # Standard data type input checks
    assert all([isinstance(i, MonitoringStation) for i in stations])

    # Get a set of all the towns from all the stations, removing duplicates
    towns = {getattr(s, 'town', None) for s in stations}

    # For each town listed, add all its associated stations.
    town_dict = {town: list(filter(lambda s: getattr(s, 'town', None) == town and       # noqa
        getattr(s, 'latest_level', None) is not None and s.typical_range_consistent(),
        stations)) for town in towns}

    # Sanitise lists
    town_dict.pop(None, None)

    # Sort the dictionary by the number of stations each town contains
    return dict(sorted(town_dict.items(), key=lambda x: len(x[1]), reverse=True))
