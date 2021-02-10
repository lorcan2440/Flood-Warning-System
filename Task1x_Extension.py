'''
Extension 1 Bokeh maps:
https://docs.bokeh.org/en/latest/docs/user_guide/geo.html

Extension 3 source
https://www.freecodecamp.org/news/python-property-decorator/
'''

from floodsystem.stationdata import build_station_list
from floodsystem.geo import display_stations_on_map


def run():
    ''' Requirements for Task 1 Extension 1 '''

    stations = build_station_list()
    display_stations_on_map(stations)


if __name__ == "__main__":
    print("\n *** Task 1 Extension 1: CUED Part IA Flood Warning System *** \n")
    run()
