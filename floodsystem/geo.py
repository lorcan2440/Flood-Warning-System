'''
This module contains a collection of functions related to
geographical data.
'''

# pylint: disable=relative-beyond-top-level, no-name-in-module

from .utils import sorted_by_key, haversine_vector, Unit
from .station import MonitoringStation


def stations_by_distance(stations: list[MonitoringStation],
        p: tuple[float]) -> list[tuple[MonitoringStation, float]]:
    '''
    Returns a list of stations, sorted by their distance from a given geographical point.

    #### Arguments

    `stations` (list): list of input stations
    `p` (tuple): (latitude, longitude) in degrees of a point to compare distances to

    #### Returns

    list[tuple[MonitoringStation, float]]: list of (station, distance in kilometres)
    '''

    # preserve original order in case of other scripts running at the same time
    _stations = stations
    ref_points, station_points = [p for i in range(len(_stations))], [s.coord for s in _stations]
    my_data = zip(_stations, list(haversine_vector(ref_points, station_points, unit=Unit.KILOMETERS)))
    del _stations

    # sort by distance (second item in each list)
    return sorted_by_key(my_data, 1)


def stations_within_radius(stations: list[MonitoringStation],
        centre: tuple[float], r: float) -> list[MonitoringStation]:
    '''
    Finds the list of stations within a given distance of a geographical point.

    #### Arguments

    `stations` (list[MonitoringStation]): list of input stations
    `centre` (tuple[float]): (latitude, longitude) in degrees of centre point
    `r` (float): radial distance in kilometres to get stations within

    #### Returns

    list[MonitoringStation]: list of output stations within range
    '''

    sorted_stations = stations_by_distance(stations, centre)

    return [s[0] for s in sorted_stations if s[1] <= r]


def rivers_with_station(stations: list) -> set[str]:
    '''
    Finds all rivers associated with the given stations.

    #### Arguments

    `stations` (list): list of input stations

    #### Returns

    set[str]: unique river names of each station
    '''

    rivers = {s.river for s in stations} - {None}

    return rivers


def stations_by_river(stations: list) -> dict[str, list[MonitoringStation]]:
    '''
    Maps river names to stations on each river.

    #### Arguments

    `stations` (list): list of input stations

    #### Returns

    dict[str, list[MonitoringStation]]: mapping of river name to a list of all stations on that river
    '''

    rivers = rivers_with_station(stations)

    river_dict = {river: list(filter(lambda s: s.river == river, stations))
        for river in rivers}

    return river_dict


def rivers_by_station_number(stations: list, n: int) -> list[tuple[str, int]]:
    '''
    Finds a list of the most populated rivers in terms of the number of stations on the river.

    #### Arguments

    `stations` (list): list of input stations
    `n` (int): maximum number of rivers to include

    #### Returns

    list[tuple[str, int]]: list of (river name, number of stations), sorted descending

    #### Raises

    `ValueError`: if number of rivers is not a positive integer
    '''

    if not n >= 1:
        raise ValueError('Number of stations must be positive')

    river_names = rivers_with_station(stations)
    river_dict = stations_by_river(stations)

    river_num_list = sorted_by_key([(r, len(river_dict[r])) for r in river_names], 1, reverse=True)
    end_num = sorted(list({r[1] for r in river_num_list}), reverse=True)[n - 1]

    return [(r, n) for r, n in river_num_list if r is not None and n >= end_num]


def stations_by_town(stations: list) -> dict[str, list[MonitoringStation]]:
    '''
    Maps town names to the stations in each town.

    #### Arguments

    `stations` (list): list of input stations

    #### Returns

    dict[str, list[MonitoringStation]]: mapping of town name to a list of all stations in that town
    '''

    # Get a set of all the towns from all the stations, removing duplicates
    towns = {s.town for s in stations}

    # For each town listed, add all its associated stations.
    town_dict = {town: list(filter(lambda s: s.town == town and       # noqa
        s.latest_level is not None and s.typical_range_consistent(),
        stations)) for town in towns}

    # Sanitise lists
    town_dict.pop(None, None)

    # Sort the dictionary by the number of stations each town contains
    return dict(sorted(town_dict.items(), key=lambda x: len(x[1]), reverse=True))
