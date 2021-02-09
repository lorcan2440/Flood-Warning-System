"""
This module provides functionality for retrieving real-time and
latest time history level data
"""

from .station import inconsistent_typical_range_stations
from .station import MonitoringStation


def stations_level_over_threshold(stations: list, tol):

    '''
    Returns a list of tuples. The first element of
    each tuple is a MonitoringStation object and the
    second element is the current relative water level
    at that station.

    Only stations with consistent range data are considered,
    and only stations with relative level above tol are added.
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

    # Eliminate stations which are invalid due to having inconsistent range data
    # Also eliminate stations which have not been updated with a 'latest_level'
    data = set(stations) - set(inconsistent_typical_range_stations(stations))
    data -= {s for s in stations if s.latest_level is None or not hasattr(s, 'latest_level')}

    # Return the remaining stations and their relative level where it is higher than tol
    # and sort in descending order of level
    return sorted([(s, s.relative_water_level()) for s in data if s.relative_water_level() > tol],
                key=lambda x: x[1], reverse=True)
