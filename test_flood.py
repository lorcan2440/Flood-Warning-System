'''
Unit tests for the flood module.
'''

from floodsystem.flood import stations_level_over_threshold
from floodsystem.station import MonitoringStation


def test_stations_level_over_threshold():

    stations = [
        MonitoringStation('station-1', None, None, None, (0, 10), None, None),
        MonitoringStation('station-2', None, None, None, (0, 10), None, None),
        MonitoringStation('station-3', None, None, None, (0, 20), None, None),
        MonitoringStation('station-4', None, None, None, (20, 10), None, None),
        MonitoringStation('station-5', None, None, None, (None, 10), None, None),
        MonitoringStation('station-6', None, None, None, None, None, None),
    ]

    setattr(stations[0], 'latest_level', 6)
    setattr(stations[1], 'latest_level', 5)
    setattr(stations[2], 'latest_level', 5)
    setattr(stations[3], 'latest_level', 0)
    setattr(stations[4], 'latest_level', '10')
    setattr(stations[5], 'latest_level', -1)

    TEST_TOL = 0.5
    assert set(stations_level_over_threshold(stations, TEST_TOL)) == {(stations[0], 0.6)}

    TEST_TOL = None
    _bad_input = False
    try:
        _bad_input = stations_level_over_threshold(stations, TEST_TOL)
    except AssertionError:
        assert True
        _bad_input = True
    finally:
        # The additional check is necessary because if the function runs without error,
        # the program will jump to here and would not trigger any "assert"s.
        assert isinstance(_bad_input, bool) and _bad_input
