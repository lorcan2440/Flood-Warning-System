'''
Unit tests for the map_plotting module.
'''

# pylint: disable=import-error

import import_helper  # noqa

from floodsystem.map_plotting import display_stations_on_map
from floodsystem.station import MonitoringStation


def test_display_stations_on_map():

    stations = [
        MonitoringStation('Station_in_Leeds', None, None, (53.8, -1.55), None, None, None),
        MonitoringStation('Station_in_Cambridge', None, None, (52.205, 0.12), None, None, None),
    ]

    test_image = display_stations_on_map(stations, return_image=True)

    # Check that the image generated exists (cannot use exact value as data changes)
    # Not easy to test this rigorously
    assert hash(test_image) > 1
