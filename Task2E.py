# Copyright (C) 2018 Garth N. Wells
#
# SPDX-License-Identifier: MIT

import datetime

from floodsystem.datafetcher import fetch_measure_levels
from floodsystem.stationdata import build_station_list, update_water_levels
from floodsystem.flood import stations_highest_rel_level
from floodsystem.plot import plot_water_levels


def run():

    # Set input parameters
    N = 5
    dt = datetime.timedelta(10)

    # Build list of stations
    stations = build_station_list()
    update_water_levels(stations)
    high_stations = stations_highest_rel_level(stations, N)

    dates, levels = {}, {}
    for s in high_stations:
        data = fetch_measure_levels(s.measure_id, dt)
        dates.update({s.name: data[0]})
        levels.update({s.name: data[1]})

    plot_water_levels(high_stations, dates, levels)


if __name__ == "__main__":
    print("\n *** Task 2D: CUED Part IA Flood Warning System *** \n")
    run()
