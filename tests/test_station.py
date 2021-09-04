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
    s = MonitoringStation(s_id, m_id, label, coord, trange, river, town)

    assert s.station_id == s_id
    assert s.measure_id == m_id
    assert s.name == label
    assert s.coord == coord
    assert s.typical_range == trange
    assert s.river == river
    assert s.town == town


def test_typical_range_consistent():

    good_station = MonitoringStation("good-id", None, None, None, (-1, 1), None, None)
    bad_station_1 = MonitoringStation("bad-id-1", None, None, None, (1, -1), None, None)
    bad_station_2 = MonitoringStation("bad-id-2", None, None, None, (None, -1), None, None)
    bad_station_3 = MonitoringStation("bad-id-3", None, None, None, None, None, None)

    assert good_station.typical_range_consistent()
    assert not bad_station_1.typical_range_consistent()
    assert not bad_station_2.typical_range_consistent()
    assert not bad_station_3.typical_range_consistent()


def test_inconsistent_typical_range_stations():

    stations = [
        MonitoringStation('good-station-1', None, None, None, (2, 4), None, None),
        MonitoringStation('boundary-station', None, None, None, (0, 0), None, None),  # Should not be allowed
        MonitoringStation('bad-station-1', None, None, None, (42, 10), None, None),
        MonitoringStation('bad-station-2', None, None, None, (None, 4), None, None),
        MonitoringStation('bad-station-3', None, None, None, None, None, None)
    ]

    bad_stations = inconsistent_typical_range_stations(stations)

    # Check there are less bad stations than stations and all fail the original check
    assert 0 <= len(bad_stations) <= len(stations)
    assert all([not b_s.typical_range_consistent() for b_s in bad_stations])
    # Check with correct result
    assert set(bad_stations) == {stations[1], stations[2], stations[3], stations[4]}


def test_relative_water_level():

    stations = [
        MonitoringStation('good-station-1', None, None, None, (0, 10), None, None),
        MonitoringStation('good-station-2', None, None, None, (10, 20), None, None),
        MonitoringStation('good-station-3', None, None, None, (-10, 0), None, None),
        MonitoringStation('bad-station-1', None, None, None, (10, 10), None, None),  # ZeroDivisionError
        MonitoringStation('bad-station-2', None, None, None, (10, 0), None, None),  # wrong ordering
        MonitoringStation('bad-station-3', None, None, None, (None, '10'), None, None),
        MonitoringStation('bad-station-4', None, None, None, None, None, None)
    ]

    setattr(stations[0], 'latest_level', 4)
    setattr(stations[1], 'latest_level', 22)
    setattr(stations[2], 'latest_level', -12)
    setattr(stations[3], 'latest_level', 10)
    setattr(stations[4], 'latest_level', 6)
    setattr(stations[5], 'latest_level', 2)
    setattr(stations[6], 'latest_level', 2)

    assert stations[0].relative_water_level() == 0.4
    assert stations[1].relative_water_level() == 1.2
    assert stations[2].relative_water_level() == -0.2
    assert all([stations[n].relative_water_level() is None for n in range(3, 7)])

    setattr(stations[0], 'latest_level', None)
    assert stations[0].relative_water_level() is None
