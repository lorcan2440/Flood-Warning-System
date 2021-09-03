# pylint: disable=import-error
import import_helper  # noqa

from floodsystem.geo import rivers_by_station_number
from floodsystem.stationdata import build_station_list


def run():

    ''' Requirements for Task 1E '''

    # Print the list of (river, number stations) tuples when N = 9,
    # i.e. the top 9 rivers with the most stations.

    stations = build_station_list()
    N = 9
    print(f'The top {N} list of the rivers with the most stations is \n{rivers_by_station_number(stations, N)}')


if __name__ == "__main__":
    print("\n *** Task 1E: CUED Part IA Flood Warning System *** \n")
    run()
