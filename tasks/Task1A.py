# pylint: disable=import-error
import import_helper  # noqa

from floodsystem.stationdata import build_station_list, build_rainfall_gauge_list


def run():

    # Build list of stations
    stations = build_station_list()
    gauges = build_rainfall_gauge_list()

    # Print number of stations
    print(f'Number of stations: {len(stations)}')
    print(f'Number of rainfall gauges: {len(gauges)} \n')

    # Display data from stations/gauges:
    for station in stations:
        if station.name in ['Cam']:
            print(station)

    for gauge in gauges:
        if gauge.gauge_number in ['50110']:
            print(gauge)


if __name__ == "__main__":
    print("\n *** Task 1A: CUED Part IA Flood Warning System *** \n")
    run()
