# pylint: disable=import-error
import import_helper  # noqa

import datetime

from floodsystem.datafetcher import fetch_measure_levels
from floodsystem.stationdata import build_station_list


def run():

    # Build list of stations
    stations = build_station_list()

    # Station name to find
    station_name = "Cam"

    # Find station
    try:
        station_cam = next(s for s in stations if s.name == station_name)
    except (UnboundLocalError, StopIteration):
        print("Station {} could not be found".format(station_name))
        return

    # Fetch data over past 2 days
    dt = 2
    dates, levels = fetch_measure_levels(station_cam.measure_id, dt=datetime.timedelta(days=dt))

    if dates[0] is None:
        return

    # Print level history
    for date, level in zip(dates, levels):
        print(date, level)


if __name__ == "__main__":
    print("\n *** Task 2D: CUED Part IA Flood Warning System *** \n")
    run()
