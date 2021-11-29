# pylint: disable=import-error
import import_helper  # noqa
from itertools import groupby

from floodsystem.stationdata import build_station_list, build_rainfall_gauge_list


def run():

    # Build list of stations
    stations = build_station_list()
    gauges = build_rainfall_gauge_list()

    # Print number of stations
    print(f'Number of stations: {len(stations)}')

    station_types = {k: list(v) for k, v in groupby(stations, key=lambda s: (s.is_tidal, s.is_groundwater))}
    river_stations = station_types[(False, False)]
    tidal_stations = station_types[(True, False)]
    groundwater_stations = station_types[(False, True)]
    print(f'\t of which river-level: {len(river_stations)}')
    print(f'\t of which tidal: {len(tidal_stations)}')
    print(f'\t of which groundwater: {len(groundwater_stations)} \n')

    print(f'Number of rainfall gauges: {len(gauges)} \n')

    # Display data from stations/gauges:
    for station in stations:
        if station.name in ['Aldershot']:
            print(station)

    for gauge in gauges:
        if gauge.gauge_number in ['50110']:
            print(gauge)


if __name__ == "__main__":
    print("\n *** Task 1A: CUED Part IA Flood Warning System *** \n")
    run()
