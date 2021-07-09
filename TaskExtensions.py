''' 
Info sources:

Extension 1.1, 2.1 and 2.2: Bokeh maps

https://docs.bokeh.org/en/latest/docs/user_guide/geo.html

Extension 1.2, 2.3 and 2.4: Extracting data from JSON files

https://stackabuse.com/reading-and-writing-json-to-a-file-in-python/

Extension 1.3: encapsulation using property decorators

https://www.freecodecamp.org/news/python-property-decorator/
https://www.youtube.com/watch?v=dzmYoSzL8ok
https://stackoverflow.com/questions/32041706/function-to-define-the-property-for-multiple-attributes
'''

from floodsystem.stationdata import build_station_list, update_water_levels
from floodsystem.geo import display_stations_on_map


def run():

    stations = build_station_list()
    update_water_levels(stations)
    display_stations_on_map(stations)


if __name__ == "__main__":
    print("\n *** Extensions: CUED Part IA Flood Warning System *** \n")
    run()
