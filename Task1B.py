from floodsystem.geo import stations_by_distance
from floodsystem.stationdata import build_station_list

def run():
    CAMBRIDGE_CITY_CENTRE = (52.2053, 0.1218)
    stations_distances = stations_by_distance(build_station_list(), CAMBRIDGE_CITY_CENTRE)
    closest_stations = stations_distances[:10]
    furthest_stations = stations_distances[-10:]

    print('The 10 closest stations are (distances in kilometers):')
    for (station, distance) in closest_stations:
        print((station.name, station.town, distance))

    print('\n')

    print('The 10 furthest stations are (distances in kilometers):')
    for (station, distance) in furthest_stations:
        print((station.name, station.town, distance))


if __name__ == "__main__":
    print("*** Task 1B: CUED Part IA Flood Warning System *** \n")
    run()

