'''
Unit tests for the geo module.
'''

from floodsystem.geo import stations_by_distance
from floodsystem.geo import stations_within_radius
from floodsystem.geo import rivers_with_station
from floodsystem.geo import stations_by_river
from floodsystem.geo import rivers_by_station_number
from floodsystem.geo import display_stations_on_map

from floodsystem.station import MonitoringStation


def test_stations_by_distance():

    TEST_COORD = (5, 5)

    # Test 1: valid inputs
    stations = [
        MonitoringStation('near-station-1', None, None, (1, 0), None, None, None),
        MonitoringStation('near-station-2', None, None, (-1, 1.5), None, None, None),
        MonitoringStation('far-station-1', None, None, (20, 40), None, None, None),
        MonitoringStation('far-station-2', None, None, (0, 30.1234), None, None, None),
        MonitoringStation('boundary-station', None, None, (-5, -5), None, None, None),
    ]

    assert [(s.station_id, round(d)) for (s, d) in stations_by_distance(stations, TEST_COORD)] == [
        ('near-station-1', 711), ('near-station-2', 772), ('boundary-station', 1572),
        ('far-station-2', 2845), ('far-station-1', 4135)]

    # Test 2: invalid inputs
    stations = [
        MonitoringStation('near-station-1', None, None, (1, 0), None, None, None),
        MonitoringStation('bad-station', None, None, None, None, None, None),
    ]

    try:
        stations_by_distance(stations, TEST_COORD)
        assert False
    except (TypeError, IndexError):
        assert True


def test_stations_within_radius():

    TEST_COORD = (5, 5)
    TEST_DISTANCE = 1571.53666171434

    stations = [
        MonitoringStation('near-station-1', None, None, (1, 0), None, None, None),
        MonitoringStation('near-station-2', None, None, (-1, 1.5), None, None, None),
        MonitoringStation('far-station-1', None, None, (20, 40), None, None, None),
        MonitoringStation('far-station-2', None, None, (0, 30.1234), None, None, None),
        MonitoringStation('boundary-station', None, None, (-5, -5), None, None, None),
    ]

    result = stations_within_radius(stations, TEST_COORD, TEST_DISTANCE)

    assert stations[0] in result
    assert stations[1] in result
    assert stations[4] in result  # on the boundary: should be included
    assert not stations[2] in result
    assert not stations[3] in result


def test_rivers_with_station():

    stations = [
        MonitoringStation('station-1', None, None, None, None, 'river-A', None),
        MonitoringStation('station-2', None, None, None, None, 'river-B', None),
        MonitoringStation('station-3', None, None, None, None, 'river-C', None),
        MonitoringStation('station-4', None, None, None, None, 'river-D', None),
        MonitoringStation('station-5', None, None, None, None, 'river-D', None),
        MonitoringStation('station-6', None, None, None, None, 'river-E', None),
    ]

    result = rivers_with_station(stations)
    assert result == {'river-A', 'river-B', 'river-C', 'river-D', 'river-E'}


def test_stations_by_river():

    import itertools

    stations = [
        MonitoringStation('station-1', None, None, None, None, 'river-A', None),
        MonitoringStation('station-2', None, None, None, None, 'river-B', None),
        MonitoringStation('station-3', None, None, None, None, 'river-C', None),
        MonitoringStation('station-4', None, None, None, None, 'river-D', None),
        MonitoringStation('station-5', None, None, None, None, 'river-D', None),
        MonitoringStation('station-6', None, None, None, None, 'river-E', None),
    ]

    river_dict = stations_by_river(stations)

    # Check all keys are string, all values are lists, and all items in all lists are MonitoringStation(s)
    assert all([isinstance(i, str) for i in list(river_dict.keys())])
    assert all([isinstance(i, list) for i in list(river_dict.values())])
    assert all([isinstance(i[0], MonitoringStation) for i in list(itertools.chain(river_dict.values()))])
    # Compare with correct result
    assert river_dict == {
        'river-A': [stations[0]], 'river-B': [stations[1]], 'river-C': [stations[2]],
        'river-D': [stations[3], stations[4]], 'river-E': [stations[5]]
    }


def test_rivers_by_station_number():

    N = 2
    stations = [
        MonitoringStation('station-1', None, None, None, None, 'river-A', None),
        MonitoringStation('station-2', None, None, None, None, 'river-A', None),
        MonitoringStation('station-3', None, None, None, None, 'river-B', None),
        MonitoringStation('station-4', None, None, None, None, 'river-B', None),
        MonitoringStation('station-5', None, None, None, None, 'river-B', None),
        MonitoringStation('station-6', None, None, None, None, 'river-C', None),
        MonitoringStation('station-7', None, None, None, None, 'river-C', None),
        MonitoringStation('station-8', None, None, None, None, 'river-C', None),
        MonitoringStation('station-9', None, None, None, None, 'river-D', None),
        MonitoringStation('station-10', None, None, None, None, 'river-D', None),
        MonitoringStation('station-11', None, None, None, None, 'river-D', None),
        MonitoringStation('station-12', None, None, None, None, 'river-E', None),
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


def test_display_stations_on_map():

    stations = [
        MonitoringStation('Station_in_Leeds', None, None, (53.8, -1.55), None, None, None),
        MonitoringStation('Station_in_Cambridge', None, None, (52.205, 0.12), None, None, None),
    ]

    test_image = display_stations_on_map(stations, return_image=True)

    # Check that the image generated exists (cannot use exact value as data changes)
    # Not easy to test this rigorously
    assert hash(test_image) > 1
