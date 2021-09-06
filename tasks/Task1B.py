# pylint: disable=import-error
import import_helper  # noqa

from floodsystem.geo import stations_by_distance
from floodsystem.station_data import build_station_list


def run():

    # Obtain the 10 closest and furthest stations in (station, distance) format
    # where station is an instance of MonitoringStation
    CAMBRIDGE_CITY_CENTRE = (52.2053, 0.1218)
    stations_distances = stations_by_distance(build_station_list(), CAMBRIDGE_CITY_CENTRE)
    closest_stations = stations_distances[:10]
    furthest_stations = stations_distances[-10:]

    # Print the closest stations (name, town, distance)
    print('The 10 closest stations are (distances in kilometers):')
    for (station, distance) in closest_stations:
        print((station.name, station.town, distance))

    # Newline for readability
    print('\n')

    # Print the furthest stations (name, town, distance)
    print('The 10 furthest stations are (distances in kilometers):')
    for (station, distance) in furthest_stations:
        print((station.name, station.town, distance))


if __name__ == "__main__":
    print("\n *** Task 1B: CUED Part IA Flood Warning System *** \n")
    run()
