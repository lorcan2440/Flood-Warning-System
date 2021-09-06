# pylint: disable=import-error
import import_helper  # noqa

from floodsystem.station_data import build_station_list


def run():

    # Build list of stations
    stations = build_station_list()

    # Print number of stations
    print(f"Number of stations: {len(stations)} \n")

    # Display data from 3 stations:
    for station in stations:
        if station.name in [
                'Bourton Dickler', 'Surfleet Sluice', 'Gaw Bridge'
        ]:
            print(station)


if __name__ == "__main__":
    print("\n *** Task 1A: CUED Part IA Flood Warning System *** \n")
    run()
