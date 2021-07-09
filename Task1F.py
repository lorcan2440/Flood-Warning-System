from floodsystem.station import inconsistent_typical_range_stations
from floodsystem.stationdata import build_station_list


def run():

    ''' Requirements for Task 1F '''

    # Obtain a list of all stations with inconsistent typical range data.
    # Print a list of station names, in alphabetical order, for stations
    # with inconsistent data.

    stations = build_station_list()
    bad_stations = sorted(inconsistent_typical_range_stations(stations), key=lambda s: s.name)

    if len(bad_stations) > 1:
        print(f'The {len(bad_stations)} stations with bad range data are: \n')
    elif len(bad_stations) == 1:
        print('The station with bad range data is: \n')
    elif len(bad_stations) == 0:
        print('There are no stations with bad range data.')

    for b_s in bad_stations:
        if b_s.typical_range is None:
            print(b_s.name + ' (Data missing)')
        else:
            print(b_s.name + ' (Wrong ordering)')


if __name__ == "__main__":
    print("\n *** Task 1F: CUED Part IA Flood Warning System *** \n")
    run()
