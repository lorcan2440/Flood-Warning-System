'''
Unit tests for the geo module.
'''

# pylint: disable=import-error

import import_helper  # noqa
import pytest

from floodsystem.geo import stations_by_distance, stations_within_radius, rivers_with_station
from floodsystem.geo import stations_by_river, rivers_by_station_number, stations_by_town
from floodsystem.station import MonitoringStation
from floodsystem.utils import flatten


def test_stations_by_distance():

    TEST_COORD = (5, 5)

    # Test 1: valid inputs
    stations = [
        MonitoringStation(None, 'near-station-1', (1, 0), None),
        MonitoringStation(None, 'near-station-2', (-1, 1.5), None),
        MonitoringStation(None, 'far-station-1', (20, 40), None),
        MonitoringStation(None, 'far-station-2', (0, 30.1234), None),
        MonitoringStation(None, 'boundary-station', (-5, -5), None),
    ]

    assert [(s.name, round(d)) for (s, d) in stations_by_distance(stations, TEST_COORD)] == [
        ('near-station-1', 711), ('near-station-2', 772), ('boundary-station', 1572),
        ('far-station-2', 2845), ('far-station-1', 4135)]

    # Test 2: invalid inputs
    stations = [
        MonitoringStation(None, 'near-station-1', (1, 0), None),
        MonitoringStation(None, 'bad-station', None, None),
    ]

    with pytest.raises((TypeError, IndexError)) as e_info:
        stations_by_distance(stations, TEST_COORD)
        print(e_info)


def test_stations_within_radius():

    TEST_COORD = (5, 5)
    TEST_DISTANCE = 1571.53666171434

    stations = [
        MonitoringStation(None, 'near-station-1', (1, 0), None),
        MonitoringStation(None, 'near-station-2', (-1, 1.5), None),
        MonitoringStation(None, 'far-station-1', (20, 40), None),
        MonitoringStation(None, 'far-station-2', (0, 30.1234), None),
        MonitoringStation(None, 'boundary-station', (-5, -5), None),
    ]

    result = stations_within_radius(stations, TEST_COORD, TEST_DISTANCE)

    assert stations[0] in result
    assert stations[1] in result
    assert stations[4] in result  # on the boundary: should be included
    assert not stations[2] in result
    assert not stations[3] in result


def test_rivers_with_station():

    stations = [
        MonitoringStation('station-1', None, None, None, river='river-A'),
        MonitoringStation('station-2', None, None, None, river='river-B'),
        MonitoringStation('station-3', None, None, None, river='river-C'),
        MonitoringStation('station-4', None, None, None, river='river-D'),
        MonitoringStation('station-5', None, None, None, river='river-D'),
        MonitoringStation('station-6', None, None, None, river='river-E'),
    ]

    result = rivers_with_station(stations)
    assert result == {'river-A', 'river-B', 'river-C', 'river-D', 'river-E'}


def test_stations_by_river():

    stations = [
        MonitoringStation('station-1', None, None, None, river='river-A'),
        MonitoringStation('station-2', None, None, None, river='river-B'),
        MonitoringStation('station-3', None, None, None, river='river-C'),
        MonitoringStation('station-4', None, None, None, river='river-D'),
        MonitoringStation('station-5', None, None, None, river='river-D'),
        MonitoringStation('station-6', None, None, None, river='river-E'),
    ]

    river_dict = stations_by_river(stations)

    # Check all keys are string, all values are lists, and all items in all lists are MonitoringStation(s)
    assert all([isinstance(i, str) for i in list(river_dict.keys())])
    assert all([isinstance(i, list) for i in list(river_dict.values())])
    assert all([isinstance(i, MonitoringStation) for i in flatten(list(river_dict.values()))])
    # Compare with correct result
    assert river_dict == {
        'river-A': [stations[0]], 'river-B': [stations[1]], 'river-C': [stations[2]],
        'river-D': [stations[3], stations[4]], 'river-E': [stations[5]]
    }


def test_rivers_by_station_number():

    N = 2
    stations = [
        MonitoringStation('station-1', None, None, None, river='river-A'),
        MonitoringStation('station-2', None, None, None, river='river-A'),
        MonitoringStation('station-3', None, None, None, river='river-B'),
        MonitoringStation('station-4', None, None, None, river='river-B'),
        MonitoringStation('station-5', None, None, None, river='river-B'),
        MonitoringStation('station-6', None, None, None, river='river-C'),
        MonitoringStation('station-7', None, None, None, river='river-C'),
        MonitoringStation('station-8', None, None, None, river='river-C'),
        MonitoringStation('station-9', None, None, None, river='river-D'),
        MonitoringStation('station-10', None, None, None, river='river-D'),
        MonitoringStation('station-11', None, None, None, river='river-D'),
        MonitoringStation('station-12', None, None, None, river='river-E')
    ]

    rivers_list = rivers_by_station_number(stations, N)

    # Check there are some rivers, and each river has some stations
    assert len(rivers_list) > 0 and all([river[1] > 0 for river in rivers_list])
    # Check list is in descending order
    assert sorted(rivers_list, key=lambda x: x[1], reverse=True) == rivers_list
    # Check the next lowest river has strictly less rivers than this one
    # i.e. check the "include duplicate numbers of rivers" works properly
    lower_rivers_list = rivers_by_station_number(stations, N + 1)

    assert rivers_list[-1][1] > lower_rivers_list[-1][1] and len(rivers_list) >= N
    assert len(lower_rivers_list) >= len(rivers_list) + 1
    # Check against the expected result, ignoring differences due to ordering of rivers
    # with equal numbers of stations
    assert set(rivers_list) == {('river-C', 3), ('river-A', 2), ('river-B', 3), ('river-D', 3)}


def test_stations_by_town():

    stations = [
        MonitoringStation(None, 'station-1', None, None, town='town-A'),
        MonitoringStation(None, 'station-2', None, None, town='town-A'),
        MonitoringStation(None, 'bad-station-1', None, None, town='town-A'),
        MonitoringStation(None, 'station-3', None, None, town='town-B'),
        MonitoringStation(None, 'bad-station-2', None, None, town='town-B'),
        MonitoringStation(None, 'station-4', None, None),
        MonitoringStation(None, None, None, None, town='empty-town'),
        MonitoringStation(None, None, None, None),
        MonitoringStation(None, None, None, None, town=())
    ]

    setattr(stations[0], 'latest_level', 10)
    setattr(stations[1], 'latest_level', 10)
    setattr(stations[2], 'latest_level', None)
    setattr(stations[3], 'latest_level', 10)
    setattr(stations[4], 'latest_level', 10)
    setattr(stations[5], 'latest_level', 10)
    setattr(stations[6], 'latest_level', 10)
    setattr(stations[7], 'latest_level', 10)
    setattr(stations[8], 'latest_level', 10)

    setattr(stations[0], 'typical_range', (5, 15))
    setattr(stations[1], 'typical_range', (5, 15))
    setattr(stations[2], 'typical_range', (5, 15))
    setattr(stations[3], 'typical_range', (5, 15))
    setattr(stations[4], 'typical_range', None)
    setattr(stations[5], 'typical_range', (5, 15))
    setattr(stations[6], 'typical_range', (5, 15))
    setattr(stations[7], 'typical_range', (5, 15))
    setattr(stations[8], 'typical_range', (5, 15))

    town_dict = stations_by_town(stations)

    # Check correct stations
    assert set(town_dict['town-A']) == {stations[0], stations[1]}
    assert set(town_dict['town-B']) == {stations[3]}
    assert set(town_dict['empty-town']) == {stations[6]}
    assert None not in town_dict
