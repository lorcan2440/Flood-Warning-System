# pylint: disable=import-error
import import_helper  # noqa

from floodsystem.stationdata import build_station_list, update_water_levels


def run():

    # Build list of stations
    stations = build_station_list()

    # Update latest level data for all stations
    update_water_levels(stations)

    # Print station and latest level for first 5 stations in list
    names = ['Bourton Dickler', 'Surfleet Sluice', 'Gaw Bridge', 'Hemingford', 'Swindon']

    for station in [s for s in stations if s.name in names]:
        print(f'Station name and current level: {station.name}, {station.latest_level}')


if __name__ == "__main__":
    print("\n *** Task 2A: CUED Part IA Flood Warning System *** \n")
    run()
