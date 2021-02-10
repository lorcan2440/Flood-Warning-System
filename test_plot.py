'''
Unit tests for the plot module.
'''

from datetime import datetime, timedelta

from floodsystem.plot import plot_water_levels
from floodsystem.station import MonitoringStation
from floodsystem.stationdata import build_station_list


def test_plot_water_levels():

    stations = [
        MonitoringStation('station-1', None, None, None, (10, 20), None, None),
        MonitoringStation('station-2', None, None, None, (5, 15), None, None),
        MonitoringStation('bad-station', None, None, None, None, None, None),
    ]

    dates = {'Station 1' :
        [datetime(2016, 12, 30), datetime(2017, 1, 1),
        datetime(2017, 1, 2), datetime(2017, 1, 3), datetime(2017, 1, 4), datetime(2017, 1, 5)],
        'Station 2' :
        [datetime(2016, 12, 30), datetime(2016, 12, 31), datetime(2017, 1, 1),
        datetime(2017, 1, 2), datetime(2017, 1, 3), datetime(2017, 1, 4), datetime(2017, 1, 5)],
        'Bad Station' :
        [datetime(2016, 12, 30), datetime(2016, 12, 31), datetime(2017, 1, 1),
        datetime(2017, 1, 2), datetime(2017, 1, 3), datetime(2017, 1, 4), datetime(2017, 1, 5)]
    }

    levels = {
        'Station 1' : [5, 5.5, 6.5, 4, 5, 7],
        'Station 2' : [3, 5, 4, 7, 5, 5.4, 5],
        'Bad Station' : [1, 2, 3, 4, 5, 6, 7]
    }

    setattr(stations[0], 'name', 'Station 1')
    setattr(stations[1], 'name', 'Station 2')
    setattr(stations[2], 'name', 'Bad Station')

    plot_water_levels(stations, dates, levels)
