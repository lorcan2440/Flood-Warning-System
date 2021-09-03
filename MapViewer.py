from floodsystem.stationdata import build_station_list, update_water_levels
from floodsystem.geo import display_stations_on_map


def run():

    stations = build_station_list()
    update_water_levels(stations)
    display_stations_on_map(stations)


if __name__ == "__main__":
    print("\n *** Extensions: CUED Part IA Flood Warning System *** \n")
    run()
