# pylint: disable=import-error
import __init__  # noqa

'''
NOTE: if switching to Dash/Plotly, consider using
https://plotly.com/python/mapbox-density-heatmaps/
to display the map as a transparent layer on the map
'''

from floodsystem.stationdata import build_station_list, update_water_levels
from floodsystem.map import stations_map_plotly


def run():

    stations = build_station_list(use_cache=False)
    update_water_levels(stations)

    map = stations_map_plotly(stations)
    map.show()


if __name__ == "__main__":
    print("\n *** Extensions: CUED Part IA Flood Warning System *** \n")
    run()
