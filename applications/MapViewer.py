# pylint: disable=import-error

import import_helper  # noqa

from floodsystem.stationdata import build_station_list, update_water_levels
from floodsystem.map import display_stations_on_map


def run():

    stations = build_station_list(use_cache=False)
    update_water_levels(stations)
    display_stations_on_map(stations, map_design='satellite')
    print(f'Displaying {len(stations)} monitoring stations on the map. \n \n'
    '>>> \t Use the toolbar on the right to interact with the map e.g. zoom, pan, save. \n'
    '>>> \t Hover over a dot to view basic info about the station. \n'
    '>>> \t Click on a dot to view the graph of the level data on the official gov.uk site.')


if __name__ == "__main__":
    print("\n *** Extensions: CUED Part IA Flood Warning System *** \n")
    run()
