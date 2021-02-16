from floodsystem.stationdata import build_station_list, update_water_levels
from floodsystem.flood import stations_highest_rel_level


def run():

    # Build list of stations
    stations = build_station_list()
    update_water_levels(stations)

    # Update latest level data for all stations
    N = 10
    high_stations = stations_highest_rel_level(stations, N)

    for s in high_stations:
        print(s.name, s.relative_water_level())


if __name__ == "__main__":
    print("\n *** Task 2C: CUED Part IA Flood Warning System *** \n")
    run()
