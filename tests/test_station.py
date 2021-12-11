'''
Unit tests for the station module.
'''

# pylint: disable=import-error
# import __init__  # noqa # uncomment if not installing package

import pytest

from floodsystem.station import inconsistent_typical_range_stations, MonitoringStation


def test_create_monitoring_station():

    # Create a station
    s_id = "test-s-id"
    m_id = "test-m-id"
    label = "some station"
    coord = (-2.0, 4.0)
    trange = (-2.3, 3.4445)
    river = "River X"
    town = "My Town"
    url_id = "hello"
    is_tidal = False
    record_range = (-5, 5)
    s = MonitoringStation(m_id, label, coord, trange,
        river=river, town=town, station_id=s_id, url_id=url_id, record_range=record_range, is_tidal=is_tidal)

    assert s.station_id == s_id
    assert s.measure_id == m_id
    assert s.name == label
    assert s.coord == coord
    assert s.typical_range == trange
    assert s.river == river
    assert s.town == town
    assert url_id in s.url and len(s.url) > len(url_id)
    assert s.is_tidal == is_tidal


@pytest.mark.parametrize("test_range, expected",
    [((-1, 1), True), ((1, -1), False), ((None, -1), False), (None, False)])
def test_typical_range_consistent(test_range: tuple, expected: bool):

    assert MonitoringStation(None, None, None, test_range).typical_range_consistent() is expected


def test_inconsistent_typical_range_stations():

    stations = [
        MonitoringStation(None, 'good-station-1', None, (2, 4)),
        MonitoringStation(None, 'boundary-station', None, (0, 0)),  # should not be allowed
        MonitoringStation(None, 'bad-station-1', None, (42, 10)),
        MonitoringStation(None, 'bad-station-2', None, (None, 4)),
        MonitoringStation(None, 'bad-station-3', None, None)
    ]

    bad_stations = inconsistent_typical_range_stations(stations)

    # Check there are less bad stations than stations and all fail the original check
    assert 0 <= len(bad_stations) <= len(stations)
    assert all([not b_s.typical_range_consistent() for b_s in bad_stations])
    # Check with correct result
    assert set(bad_stations) == {stations[1], stations[2], stations[3], stations[4]}


@pytest.mark.parametrize("test_range, test_level, expected",
    [((0, 10), 4, 0.4), ((10, 20), 22, 1.2), ((-10, 0), None, None), ((10, 10), 10, None), ((10, 0), 6, None),
    ((None, '10'), 2, None), (None, 2, None)])
def test_relative_water_level(test_range: tuple, test_level: float, expected: bool):

    assert MonitoringStation(
        None, None, None, test_range, latest_level=test_level).relative_water_level() == expected
