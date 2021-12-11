# pylint: disable=import-error
import __init__  # noqa # uncomment if not installing package

from floodsystem.stationdata import build_station_list, build_rainfall_gauge_list


def run():

    # Build list of stations
    stations, nums = build_station_list(return_numbers=True)
    gauges = build_rainfall_gauge_list()

    # Print number of stations
    print(f'Number of stations: \t \t {len(stations)}')
    print(f'\t of which river-level: \t {nums["River Level"]}')
    print(f'\t of which tidal: \t \t {nums["Tidal"]}')
    print(f'\t of which groundwater: \t {nums["Groundwater"]} \n')

    print(f'Number of rainfall gauges: \t {len(gauges)} \n')

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
