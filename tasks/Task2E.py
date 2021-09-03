# pylint: disable=import-error
import import_helper  # noqa

import datetime
import warnings

from floodsystem.datafetcher import fetch_measure_levels
from floodsystem.stationdata import build_station_list, update_water_levels
from floodsystem.flood import stations_highest_rel_level
from floodsystem.plot import plot_water_levels

''' ignore warnings '''
# warnings.simplefilter()


def run():

    # Set input parameters
    N = 5  # top 5 stations
    dt = datetime.timedelta(10)  # 10 days

    # Build list of stations with the highest current relative water levels
    stations = build_station_list()
    update_water_levels(stations)
    high_stations = stations_highest_rel_level(stations, N)

    # Fetch the dates and levels from each station
    flags = []
    dates, levels = {}, {}
    for s in high_stations:
        data = fetch_measure_levels(s.measure_id, dt)
        # Sanitise input data
        for index in range(len(data[1])):
            if not isinstance(data[1][index], float):
                data[1][index] = data[1][index][1]
                flags.append(s.name)
            if data[1][index] < 0:
                data[1][index] = data[1][index - 1]
                flags.append(s.name)

        dates.update({s.name: data[0]})
        levels.update({s.name: data[1]})

    for s in set(flags):
        warnings.warn(f'Warning: The data for {s} may be unreliable.', RuntimeWarning)

    # Plot the graphs
    plot_water_levels(high_stations, dates, levels, as_subplots=False)


if __name__ == "__main__":
    print("\n *** Task 2E: CUED Part IA Flood Warning System *** \n")
    run()
