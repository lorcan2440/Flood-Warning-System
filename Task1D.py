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
    print('Number of rivers with at least one monitoring station: {}'.format(len(rivers)))
    print('First 10 in alphabetical order: {} \n'.format(sorted(list(rivers))[:10]))

    river_dict = stations_by_river(stations)
    wanted_rivers = ["River Aire", "River Cam", "River Thames"]
    for river in wanted_rivers:
        print('The stations on {} are: \n\n{}\n'.format(river, sorted([s.name for s in river_dict[river]])))


if __name__ == "__main__":
    print("*** Task 1D: CUED Part IA Flood Warning System *** \n")
    run()
