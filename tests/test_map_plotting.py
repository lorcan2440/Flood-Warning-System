'''
Unit tests for the map_plotting module.
'''

# pylint: disable=import-error

import import_helper  # noqa

from floodsystem.map_plotting import display_stations_on_map
from floodsystem.station import MonitoringStation


def test_display_stations_on_map():

    stations = [
        MonitoringStation(None, None, 'Green_Station_Leeds', (53.8, -1.55), (10, 20), None, "Leeds"),
        MonitoringStation(None, None, 'Grey_Station_Cambridge', (52.205, 0.12), None, None, "Cambridge"),
        MonitoringStation(None, None, 'Negative_Station', (54, 0.6), (1, 3), None, None),
        MonitoringStation(None, None, 'Unset_latest', (57, 2), (10, 20), None, None),
        MonitoringStation(None, None, 'Yellow_station', (54, -7), (10, 20), None, None),
        MonitoringStation(None, None, 'Orange_station', (54, -7.3), (10, 20), None, None),
        MonitoringStation(None, None, 'Red_station', (54, -7.6), (10, 20), None, None),
        MonitoringStation(None, None, 'Unset_coords', None, (10, 20), None, None),
    ]

    setattr(stations[0], "latest_level", 12)
    setattr(stations[1], "latest_level", None)
    setattr(stations[2], "latest_level", -0.4)
    setattr(stations[4], "latest_level", 22)
    setattr(stations[5], "latest_level", 29)
    setattr(stations[6], "latest_level", 36)

    # test returning
    test_image = display_stations_on_map(stations, return_image=True)
    assert hash(test_image) > 1

    # test default design
    display_stations_on_map(stations)

    # test custom design
    display_stations_on_map(stations, map_design="CARTODBPOSITRON_RETINA")
