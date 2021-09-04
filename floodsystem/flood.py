'''
This module provides functions for getting
stations by their water levels.
'''

# pylint: disable=import-error, relative-beyond-top-level

from .station import inconsistent_typical_range_stations
from .station import MonitoringStation


def stations_level_over_threshold(stations: list, tol: float) -> list[tuple[MonitoringStation, float]]:

    '''
    Returns a list of tuples. The first element of
    each tuple is a MonitoringStation object and the
    second element is the current relative water level
    at that station.

    Only stations with consistent range data are considered,
    and only stations with relative level above `tol` are added.
    '''

    # Standard data type input checks.
    assert isinstance(stations, list) and all([isinstance(i, MonitoringStation) for i in stations])
    assert isinstance(tol, (int, float))
    # Check all objects are hashable so they can be used to construct the sets below
    try:
        _hashable = all([isinstance(hash(s), int) for s in stations])
        if _hashable:
            assert True
    except TypeError:
        assert False

    # Eliminate stations which are invalid due to having inconsistent range data or undefined values
    data = set(stations) - set(inconsistent_typical_range_stations(stations))
    data -= set(filter(lambda s: s.latest_level is None or not hasattr(s, 'latest_level')
        or s.relative_water_level() is None, stations))

    # Return the remaining stations and their relative level where it is higher than tol
    # and sort in descending order of level
    return sorted([(s, s.relative_water_level()) for s in data if s.relative_water_level() > tol],
                key=lambda x: x[1], reverse=True)


def stations_highest_rel_level(stations: list, n) -> list[MonitoringStation]:

    '''
    Returns a list of the `n` stations (objects) at which the water level,
    relative to the typical range, is highest. The values are assumed
    to be all unique so the length of the return list is always `n`.
    '''

    # Standard data type and bounds input checks
    assert isinstance(stations, list) and all([isinstance(i, MonitoringStation) for i in stations])
    assert isinstance(n, int)

    # Get a descending list of stations with a known level
    # HACK: implemented as being above -inf and select the first `n` objects
    valid_stations = stations_level_over_threshold(stations, float('-inf'))

    if not 0 <= n <= len(valid_stations):
        raise ValueError(f'''N must be an positive integer, and no more
                        than the length of the list of valid stations
                        ({len(valid_stations)})''')

    return [s[0] for s in valid_stations][:n]
