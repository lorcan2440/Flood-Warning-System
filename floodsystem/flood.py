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

    # Eliminate stations which are invalid due to having inconsistent range data or undefined values
    data = set(stations) - set(inconsistent_typical_range_stations(stations))
    data -= {s for s in stations if any([s.latest_level is None,
                                        not hasattr(s, 'latest_level'),
                                        s.relative_water_level() is None])}

    # Return the remaining stations and their relative level where it is higher than tol
    # and sort in descending order of level
    return sorted([(s, s.relative_water_level()) for s in data if s.relative_water_level() > tol],
                key=lambda x: x[1], reverse=True)


def stations_highest_rel_level(stations, N):

    '''
    Returns a list of the N stations (objects) at which the water level,
    relative to the typical range, is highest. The values are assumed
    to be all unique so the length of the return list is always N.
    '''

    # Standard data type and bounds input checks
    assert isinstance(stations, list) and all([isinstance(i, MonitoringStation) for i in stations])
    assert 0 <= N <= len(stations)

    # Get a descending list of stations with a known level (implemented as being above
    # an effective -infinity) and select the first N objects
    _NEG_INF = -1e300
    return [s[0] for s in stations_level_over_threshold(stations, _NEG_INF)][:N]
