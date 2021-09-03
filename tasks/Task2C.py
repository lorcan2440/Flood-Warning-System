# pylint: disable=import-error
import import_helper  # noqa

from floodsystem.stationdata import build_station_list, update_water_levels
from floodsystem.flood import stations_highest_rel_level


def run():

    # Build and update list of stations
    stations = build_station_list()
    update_water_levels(stations)

    # Fetch the highest 10 stations by relative level
    N = 10
    high_stations = stations_highest_rel_level(stations, N)

    for s in high_stations:
        print(s.name, s.relative_water_level())


if __name__ == "__main__":
    print("\n *** Task 2C: CUED Part IA Flood Warning System *** \n")
    run()
