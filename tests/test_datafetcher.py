'''
Unit tests for the stationdata module.
'''

# pylint: disable=import-error

import datetime
import import_helper  # noqa

from floodsystem.datafetcher import fetch_measure_levels
from floodsystem.stationdata import build_station_list


def test_build_station_list():

    # Build list of stations
    stations = build_station_list()

    assert len(stations) > 0

    station_cam = list(filter(lambda s: s.name == 'Cam', stations))[0]

    # Assert that station is found
    assert station_cam

    # Fetch data over past 2 days
    dt = 2
    dates2, levels2 = fetch_measure_levels(
        station_cam.measure_id, dt=datetime.timedelta(days=dt))
    assert len(dates2) == len(levels2)

    # Fetch data over past 10 days
    dt = 10
    dates10, levels10 = fetch_measure_levels(
        station_cam.measure_id, dt=datetime.timedelta(days=dt))
    assert len(dates10) == len(levels10)
    assert len(dates10) > len(levels2)
