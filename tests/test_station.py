'''
Unit tests for the station module.
'''

# pylint: disable=import-error

import import_helper  # noqa

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


def test_typical_range_consistent():

    good_station = MonitoringStation(None, "good", None, (-1, 1))
    bad_station_1 = MonitoringStation(None, "bad-1", None, (1, -1))
    bad_station_2 = MonitoringStation(None, "bad-2", None, (None, -1))
    bad_station_3 = MonitoringStation(None, "bad-3", None, None)

    assert good_station.typical_range_consistent()
    assert not bad_station_1.typical_range_consistent()
    assert not bad_station_2.typical_range_consistent()
    assert not bad_station_3.typical_range_consistent()


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


def test_relative_water_level():

    stations = [
        MonitoringStation(None, 'good-station-1', None, (0, 10), latest_level=4),
        MonitoringStation(None, 'good-station-2', None, (10, 20), latest_level=22),
        MonitoringStation(None, 'good-station-3', None, (-10, 0), latest_level=None),
        MonitoringStation(None, 'bad-station-1', None, (10, 10), latest_level=10),  # ZeroDivisionError
        MonitoringStation(None, 'bad-station-2', None, (10, 0), latest_level=6),  # wrong ordering
        MonitoringStation(None, 'bad-station-3', None, (None, '10'), latest_level=2),
        MonitoringStation(None, 'bad-station-4', None, None, latest_level=2)
    ]

    assert stations[0].relative_water_level() == 0.4
    assert stations[1].relative_water_level() == 1.2
    assert all([stations[n].relative_water_level() is None for n in range(2, 7)])
