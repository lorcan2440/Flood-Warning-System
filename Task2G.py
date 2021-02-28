import numpy as np

from floodsystem.stationdata import build_station_list, update_water_levels
from floodsystem.geo import stations_by_town


def run():

    # Build a dictionary of stations listed by the town they are in
    stations = build_station_list()
    update_water_levels(stations)
    town_dict = stations_by_town(stations)

    town_danger_level = {}
    for town, stations in town_dict.items():
        town_danger_level.update({town: np.average([s.relative_water_level() for s in stations])})

    towns_by_severity = {'severe': [t for t in town_danger_level if town_danger_level[t] >= 2],
                        'high': [t for t in town_danger_level if 1.5 <= town_danger_level[t] < 2],
                        'moderate': [t for t in town_danger_level if 0.9 <= town_danger_level[t] < 1.5],
                        'low': [t for t in town_danger_level if town_danger_level[t] < 0.9]}

    for tier in towns_by_severity:
        print(f'''Towns with a "{tier.upper()}" level flood warning are:
            \n{towns_by_severity[tier]} \n''')


if __name__ == '__main__':
    print("\n *** Task 2G: CUED Part IA Flood Warning System *** \n")
    run()
