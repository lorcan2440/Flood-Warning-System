'''
This module provides functions for getting
stations by their water levels.
'''

# local imports
try:
    from .station import MonitoringStation, inconsistent_typical_range_stations
except ImportError:
    from .station import MonitoringStation, inconsistent_typical_range_stations


def stations_level_over_threshold(stations: list, tol: float) -> list[tuple[MonitoringStation, float]]:
    '''
    Filters stations to those which have a relative water level (latest level
    as a fraction of the typical range) above a given threshold.

    #### Arguments

    `stations` (list): list of stations to be filtered
    `tol` (float): cutoff value for relative water level

    #### Returns

    list[tuple[MonitoringStation, float]]: list of (station, relative water level) tuples
    '''

    # Eliminate stations which are invalid due to having inconsistent range data or undefined values
    data = set(stations) - set(inconsistent_typical_range_stations(stations))
    data -= set(filter(lambda s: s.latest_level is None or not hasattr(s, 'latest_level')
        or s.relative_water_level() is None, stations))

    high_stations = [(s, s.relative_water_level()) for s in data if s.relative_water_level() > tol]
    return sorted(high_stations, key=lambda x: x[1], reverse=True)


def stations_highest_rel_level(stations: list, num: int) -> list[MonitoringStation]:
    '''
    Finds the stations with the highest relative water level.

    #### Arguments

    `stations` (list): list of stations to be searched
    `num` (int): number of stations to include in the list

    #### Returns

    list[MonitoringStation]: list of stations with highest relative water levels

    #### Raises

    `ValueError`: if num is not between 1 and the input length
    '''

    if not 0 <= num <= len(vs := stations_level_over_threshold(stations, float('-inf'))):
        raise ValueError('Output length must be non-negative and not more than the input length.')

    return [s[0] for s in vs][:num]
