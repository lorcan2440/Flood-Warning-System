# Copyright (C) 2018 Garth N. Wells
#
# SPDX-License-Identifier: MIT
"""Unit test for the station module"""

from floodsystem.station import inconsistent_typical_range_stations, MonitoringStation
from floodsystem.stationdata import build_station_list


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

    stations = build_station_list()
    bad_stations = inconsistent_typical_range_stations(stations)

    assert 0 <= len(bad_stations) <= len(stations)
    assert all([not b_s.typical_range_consistent() for b_s in bad_stations])
