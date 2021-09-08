# pylint: disable=import-error
import import_helper  # noqa

import datetime

from floodsystem.datafetcher import fetch_measure_levels
from floodsystem.station_data import build_station_list, update_water_levels
from floodsystem.flood import stations_highest_rel_level
from floodsystem.plot import plot_water_level_with_fit


''' ignore warnings '''
# warnings.simplefilter()


def run():

    # Set input parameters
    N = 5  # top 5 stations
    dt = datetime.timedelta(2)  # 2 days
    p = 4  # polyfit degree

    # Build list of stations with the highest current relative water levels
    stations = build_station_list()
    update_water_levels(stations)
    high_stations = stations_highest_rel_level(stations, N)

    # Fetch the dates and levels from each station and plot each
    dates, levels = {}, {}
    for s in high_stations:
        data = fetch_measure_levels(s.measure_id, dt)
        dates.update({s.name: data[0]})
        levels.update({s.name: data[1]})

        # Plot the graphs
        plot_water_level_with_fit(s, dates[s.name], levels[s.name], p, format_dates=True,
            use_proplot_style=True)


if __name__ == "__main__":
    print("\n *** Task 2F: CUED Part IA Flood Warning System *** \n")
    run()
