'''
Unit tests for the flood module.
'''

# pylint: disable=import-error
# import __init__  # noqa # uncomment if not installing package

from floodsystem.flood import stations_level_over_threshold, stations_highest_rel_level
from floodsystem.station import MonitoringStation


def test_stations_level_over_threshold():

    stations = [
        MonitoringStation(None, None, None, (0, 10), latest_level=6),
        MonitoringStation(None, None, None, (0, 10), latest_level=5),
        MonitoringStation(None, None, None, (0, 20), latest_level=5),
        MonitoringStation(None, None, None, (20, 10), latest_level=0),
        MonitoringStation(None, None, None, (None, 10), latest_level='10'),
        MonitoringStation(None, None, None, None, latest_level=-1),
    ]

    TEST_TOL = 0.5
    assert stations_level_over_threshold(stations, TEST_TOL) == [(stations[0], 0.6)]

    TEST_TOL = None
    _bad_input = False
    try:
        _bad_input = stations_level_over_threshold(stations, TEST_TOL)
    except TypeError:
        assert True
        _bad_input = True
    finally:
        assert isinstance(_bad_input, bool) and _bad_input


def test_stations_highest_rel_level():

    stations = [
        MonitoringStation(None, None, None, (0, 10), latest_level=20),
        MonitoringStation(None, None, None, (0, 10), latest_level=13),
        MonitoringStation(None, None, None, (0, 10), latest_level=None),
        MonitoringStation(None, None, None, (5, 10), latest_level=12.5),
        MonitoringStation(None, None, None, (0, 100), latest_level='10'),
        MonitoringStation(None, None, None, None, latest_level=-1),
    ]

    assert stations_highest_rel_level(stations, 2) == [stations[0], stations[3]]
