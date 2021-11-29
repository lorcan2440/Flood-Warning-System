# pylint: disable=import-error

'''
NOTE: if switching to Dash/Plotly, consider using
https://plotly.com/python/mapbox-density-heatmaps/
to display the map as a transparent layer on the map
'''

import import_helper  # noqa

from floodsystem.stationdata import build_station_list, update_water_levels, \
    build_rainfall_gauge_list, update_rainfall_levels
from floodsystem.map import display_stations_on_map


def run():

    stations = build_station_list()
    gauges = build_rainfall_gauge_list()
    update_water_levels(stations)
    update_rainfall_levels(gauges)

    display_stations_on_map(stations,
        map_design='STAMEN_TERRAIN_RETINA', filedir='applications/output', filter_station_type=None)


if __name__ == "__main__":
    print("\n *** Extensions: CUED Part IA Flood Warning System *** \n")
    run()
