# pylint: disable=import-error
import __init__  # noqa # uncomment if not installing package

import datetime

from floodsystem.datafetcher import fetch_measure_levels, fetch_rainfall_levels
from floodsystem.stationdata import build_station_list, build_rainfall_gauge_list


def run():

    # Build list of stations and gauges
    stations = build_station_list()
    gauges = build_rainfall_gauge_list()

    # Station name to find
    station_name = "Hartlepool Valley Drive"
    gauge_number = "50110"

    # Find station and gauge
    try:
        station_cam = next(s for s in stations if s.name == station_name)
    except (UnboundLocalError, StopIteration):
        print(f"Station {station_name} could not be found")
        return

    try:
        gauge_wanted = next(g for g in gauges if g.gauge_number == gauge_number)
    except (UnboundLocalError, StopIteration):
        print(f"Gauge #{gauge_number} could not be found")
        return

    # Fetch data over past 2 days
    dt = 10
    dates, levels = fetch_measure_levels(station_cam.measure_id, dt=datetime.timedelta(days=dt))

    if dates[0] is not None:
        for date, level in zip(dates, levels):
            print(date, level)

    dates, levels = fetch_rainfall_levels(gauge_wanted.measure_id, dt=datetime.timedelta(days=dt))

    if dates[0] is not None:
        for date, level in zip(dates, levels):
            print(date, level)


if __name__ == "__main__":
    print("\n *** Task 2D: CUED Part IA Flood Warning System *** \n")
    run()
