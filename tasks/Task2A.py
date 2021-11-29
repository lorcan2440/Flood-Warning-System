# pylint: disable=import-error
import import_helper  # noqa

from floodsystem.stationdata import build_station_list, update_water_levels, \
    build_rainfall_gauge_list, update_rainfall_levels


def run():

    # Build list of stations and gauges
    stations = build_station_list()
    gauges = build_rainfall_gauge_list()

    # Update latest level data for all stations and gauges
    update_water_levels(stations)
    update_rainfall_levels(gauges)

    # Print station and latest level for first 5 stations in list
    names = ['Bourton Dickler', 'Surfleet Sluice', 'Gaw Bridge', 'Hemingford', 'Swindon']

    for station in [s for s in stations if s.name in names]:
        print(f'Station name and current level: {station.name}, ' + \
            f'{station.latest_level} at {station.latest_recorded_datetime}')

    for gauge in [g for g in gauges if g.gauge_number == '50110']:
        print(f'Gauge number and current level: {gauge.gauge_number}, ' + \
            f'{gauge.latest_level} and {gauge.latest_recorded_datetime}')


if __name__ == "__main__":
    print("\n *** Task 2A: CUED Part IA Flood Warning System *** \n")
    run()
