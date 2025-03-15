# pylint: disable=import-error
import __init__  # noqa # uncomment if not installing package

from floodsystem.geo import stations_within_radius
from floodsystem.stationdata import build_station_list


def run():

    ''' Requirements for Task 1C '''

    # Obtain a list of stations within 10 km of the Cambridge
    # city centre, printing the names in alphabetical order.

    CAMBRIDGE_CITY_CENTRE = (52.2053, 0.1218)
    DISTANCE = 10

    stations = stations_within_radius(build_station_list(), CAMBRIDGE_CITY_CENTRE, DISTANCE)

    print(f'The stations within {DISTANCE} km of Cambridge City Centre are:\n')
    print(sorted([stations.name for stations in stations]))


if __name__ == "__main__":
    print("\n *** Task 1C: CUED Part IA Flood Warning System *** \n")
    run()
