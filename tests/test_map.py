'''
Unit tests for the map module.
'''

# pylint: disable=import-error
# import __init__  # noqa # uncomment if not installing package

from floodsystem.map import stations_map_bokeh
from floodsystem.station import MonitoringStation


def test_display_stations_on_map():

    stations = [
        MonitoringStation(None, 'Green_Station_Leeds', (53.8, -1.55), (10, 20), town="Leeds"),
        MonitoringStation(None, 'Grey_Station_Cambridge', (52.205, 0.12), None, town="Cambridge", river="Cam"),
        MonitoringStation(None, 'Negative_Station', (54, 0.6), (1, 3)),
        MonitoringStation(None, 'Unset_latest', (57, 2), (10, 20)),
        MonitoringStation(None, 'Yellow_station', (54, -7), (10, 20)),
        MonitoringStation(None, 'Orange_station', (54, -7.3), (10, 20)),
        MonitoringStation(None, 'Red_station', (54, -7.6), (10, 20)),
        MonitoringStation(None, 'Unset_coords', None, (10, 20)),
    ]

    setattr(stations[0], "latest_level", 12)
    setattr(stations[1], "latest_level", None)
    setattr(stations[2], "latest_level", -0.4)
    setattr(stations[4], "latest_level", 22)
    setattr(stations[5], "latest_level", 29)
    setattr(stations[6], "latest_level", 36)

    # test returning
    test_image = stations_map_bokeh(stations)
    assert hash(test_image) > 1

    # test default design
    stations_map_bokeh(stations)

    # test custom design
    stations_map_bokeh(stations, map_design="CARTODBPOSITRON_RETINA")
