'''
Unit test for the geo module.
'''

from floodsystem.geo import stations_by_distance, stations_within_radius
from floodsystem.stationdata import build_station_list


def test_stations_by_distance():

    CAMBRIDGE_CITY_CENTRE = (52.2053, 0.1218)
    stations_distances = stations_by_distance(build_station_list(), CAMBRIDGE_CITY_CENTRE)
    num_stations = len(stations_distances)

    # Ensure the stations list is not empty
    assert num_stations > 0

    # Ensure each station's distance is geq than the previous one
    # (in increasing order). The >= is required since sometimes two
    # of the same stations are listed, so gives equal distances.
    assert all([stations_distances[i + 1][1] >= stations_distances[i][1] for i in range(num_stations - 1)])


def test_stations_within_radius():

    CAMBRIDGE_CITY_CENTRE = (52.2053, 0.1218)
    TEST_DISTANCE = 10

    nearby_stations = stations_within_radius(build_station_list(), CAMBRIDGE_CITY_CENTRE, TEST_DISTANCE)

    assert len(nearby_stations) > 0  # Check there are some stations
    assert all([type(i) == str for i in nearby_stations])  # Check all items are strings
    assert sorted(nearby_stations) == nearby_stations  # Check it's sorted


test_stations_by_distance()
test_stations_within_radius()
