from floodsystem.stationdata import build_station_list, update_water_levels
from floodsystem.flood import stations_level_over_threshold


def run():

    # Build list of stations
    stations = build_station_list()
    update_water_levels(stations)

    # Update latest level data for all stations
    THRESHOLD = 0.8
    high_stations = stations_level_over_threshold(stations, THRESHOLD)

    print(f'The stations with a relative water level above {THRESHOLD} are: \n')
    for (s, level) in high_stations:
        print(s.name, level)


if __name__ == "__main__":
    print("\n *** Task 2B: CUED Part IA Flood Warning System *** \n")
    run()
