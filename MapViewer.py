from floodsystem.stationdata import build_station_list, update_water_levels
from floodsystem.map_plotting import display_stations_on_map


def run():

    stations = build_station_list()
    update_water_levels(stations)
    display_stations_on_map(stations)
    print(f'Displaying {len(stations)} monitoring stations on the map. \n'
    'Use the toolbar on the right to interact with the map e.g. zoom, pan, save. \n'
    'Hover over a dot to view basic info about the station. \n'
    'Click on a dot to view the graph of the level data on the official gov.uk site.')


if __name__ == "__main__":
    print("\n *** Extensions: CUED Part IA Flood Warning System *** \n")
    run()
