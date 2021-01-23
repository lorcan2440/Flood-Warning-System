'''
Unit test for the geo module.
'''

from floodsystem.geo import stations_by_distance
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


test_stations_by_distance()
