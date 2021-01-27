'''
Unit test for the geo module.
'''

from floodsystem.geo import stations_by_distance
from floodsystem.geo import stations_within_radius
from floodsystem.geo import rivers_with_station
from floodsystem.geo import stations_by_river
from floodsystem.geo import rivers_by_station_number

from floodsystem.stationdata import build_station_list
from floodsystem.station import MonitoringStation

from itertools import chain


def test_stations_by_distance():

    CAMBRIDGE_CITY_CENTRE = (52.2053, 0.1218)
    stations_distances = stations_by_distance(build_station_list(), CAMBRIDGE_CITY_CENTRE)
    num_stations = len(stations_distances)

    # Check there are some stations
    assert num_stations > 0
    # Check all stations >= than the previous
    # so they are in increasing order
    assert all([stations_distances[i + 1][1] >= stations_distances[i][1] for i in range(num_stations - 1)])


def test_stations_within_radius():

    CAMBRIDGE_CITY_CENTRE = (52.2053, 0.1218)
    TEST_DISTANCE = 10

    nearby_stations = stations_within_radius(build_station_list(), CAMBRIDGE_CITY_CENTRE, TEST_DISTANCE)

    # Check there are some stations
    assert len(nearby_stations) > 0
    # Check all items are strings
    assert all([type(i) == str for i in nearby_stations])
    # Check it's sorted
    assert sorted(nearby_stations) == nearby_stations


def test_rivers_with_station():

    rivers = rivers_with_station(build_station_list())

    # check there are some rivers
    assert len(rivers) > 0
    # Check all rivers are strings
    assert all([type(i) == str for i in rivers])


def test_stations_by_river():

    river_dict = stations_by_river(build_station_list())

    # check there are some rivers
    assert len(river_dict) > 0
    # Check all river keys are strings
    assert all([type(i) == str for i in list(river_dict.keys())])
    # Check all values are lists
    assert all([type(i) == list for i in list(river_dict.values())])
    # Check all values' items are MonitoringStation instances
    assert all([isinstance(i[0], MonitoringStation) for i in list(chain(river_dict.values()))])


def test_rivers_by_station_number():

    N = 2
    stations = [
        MonitoringStation('station-1', None, None, None, None, 'river-A', None),
        MonitoringStation('station-2', None, None, None, None, 'river-A', None),
        MonitoringStation('station-3', None, None, None, None, 'river-B', None),
        MonitoringStation('station-4', None, None, None, None, 'river-B', None),
        MonitoringStation('station-5', None, None, None, None, 'river-C', None),
        MonitoringStation('station-6', None, None, None, None, 'river-C', None),
        MonitoringStation('station-7', None, None, None, None, 'river-C', None),
        MonitoringStation('station-8', None, None, None, None, 'river-D', None),
        MonitoringStation('station-9', None, None, None, None, 'river-D', None),
        MonitoringStation('station-10', None, None, None, None, 'river-E', None),
        ]  # noqa

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
    # Check against the expected result
    assert rivers_list == [('river-C', 3), ('river-A', 2), ('river-B', 2), ('river-D', 2)]


test_stations_by_distance()
test_stations_within_radius()
test_rivers_with_station()
test_stations_by_river()
test_rivers_by_station_number()
