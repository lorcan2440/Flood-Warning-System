# pylint: disable=import-error
import __init__  # noqa # uncomment if not installing package

from floodsystem.geo import rivers_with_station, stations_by_river
from floodsystem.stationdata import build_station_list


def run():

    ''' Requirements for Task 1D '''

    # Print how many rivers have at least one monitoring station
    # and print the first 10 of these rivers in alphabetical order;
    # Print the names of the stations located on the following rivers
    # in alphabetical order:
    # "River Aire", "River Cam", "River Thames".

    stations = build_station_list()
    rivers = rivers_with_station(stations)
    print(f'Number of rivers with at least one monitoring station: {len(rivers)}')
    print(f'First 10 in alphabetical order: {sorted(list(rivers))[:10]} \n')

    river_dict = stations_by_river(stations)
    wanted_rivers = ["River Aire", "River Cam", "River Thames"]
    for river in wanted_rivers:
        print(f'The stations on {river} are: \n\n{sorted([s.name for s in river_dict[river]])}\n')


if __name__ == "__main__":
    print("\n *** Task 1D: CUED Part IA Flood Warning System *** \n")
    run()
