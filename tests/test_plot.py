'''
Unit tests for the plot module.
'''

# pylint: disable=import-error

import import_helper  # noqa
from datetime import datetime

from floodsystem.plot import plot_water_levels, plot_water_level_with_polyfit
from floodsystem.station import MonitoringStation


def test_plot_water_levels():

    stations = [
        MonitoringStation('station-1', None, None, None, (10, 20), None, None),
        MonitoringStation('station-2', None, None, None, (5, 15), None, None),
        MonitoringStation('station-3', None, None, None, (6, 7), None, None),
        MonitoringStation('bad-station', None, None, None, None, None, None),
    ]

    # a mixture of different amounts of dates, invalid dates and bad formats
    dates = {'Station 1':
        [datetime(2016, 12, 30), datetime(2017, 1, 1),
        datetime(2017, 1, 2), datetime(2017, 1, 3), datetime(2017, 1, 4), datetime(2017, 1, 5)],
        'Station 2':
        [datetime(2016, 12, 30), datetime(2016, 12, 31), datetime(2017, 1, 1),
        datetime(2017, 1, 2), datetime(2017, 1, 3), datetime(2017, 1, 4), datetime(2017, 1, 5)],
        'Station 3': [datetime(2016, 12, 30), datetime(2017, 1, 1),
        datetime(2017, 1, 2), datetime(2017, 1, 3), datetime(2017, 1, 4), datetime(2017, 1, 5)],
        'Bad Station':
        [datetime(2016, 12, 30), datetime(2016, 12, 31), datetime(2017, 1, 1),
        datetime(2017, 1, 2), datetime(2017, 1, 3), datetime(2017, 1, 4), datetime(2017, 1, 5)]
    }

    levels = {
        'Station 1': [5, 5.5, 6.5, 4, 5, 7],
        'Station 2': [3, 5, 4, 7, 5, 5.4, 5],
        'Station 3': [6, 6, 5.6, 5.2, 4.8, 4.9],
        'Bad Station': [1, 2, 3, 4, 5, 6, 7]
    }

    setattr(stations[0], 'name', 'Station 1')
    setattr(stations[1], 'name', 'Station 2')
    setattr(stations[2], 'name', 'Station 3')
    setattr(stations[3], 'name', 'Bad Station')

    # should run without exception
    plot_water_levels(stations, dates, levels, as_subplots=False)
    plot_water_levels(stations, dates, levels, as_subplots=True)

    # try without ProPlot
    plot_water_levels(stations, dates, levels, as_subplots=False, use_proplot_style=False)
    plot_water_levels(stations, dates, levels, as_subplots=True, use_proplot_style=False)


def test_plot_water_level_with_fit():

    stations = [
        MonitoringStation('station-1', None, None, None, (10, 20), None, None),
        MonitoringStation('station-2', None, None, None, (5, 15), None, None),
        MonitoringStation('bad-station', None, None, None, None, None, None),
    ]

    # a mixture of different amounts of dates, invalid dates and bad formats
    dates = {'Station 1':
        [datetime(2016, 12, 30), datetime(2017, 1, 1),
        datetime(2017, 1, 2), datetime(2017, 1, 3), datetime(2017, 1, 4), datetime(2017, 1, 5)],
        'Station 2':
        [datetime(2016, 12, 30), datetime(2016, 12, 31), datetime(2017, 1, 1),
        datetime(2017, 1, 2), datetime(2017, 1, 3), datetime(2017, 1, 4), datetime(2017, 1, 5)],
        'Bad Station':
        [datetime(2016, 12, 30), datetime(2016, 12, 31), datetime(2017, 1, 1),
        datetime(2017, 1, 2), datetime(2017, 1, 3), datetime(2017, 1, 4), datetime(2017, 1, 5)]
    }

    levels = {
        'Station 1': [5, 5.5, 6.5, 4, 5, 7],
        'Station 2': [3, 5, 4, 7, 5, 5.4, 5],
        'Bad Station': [1, 2, 3, 4, 5, 6, 7]
    }

    setattr(stations[0], 'name', 'Station 1')
    setattr(stations[1], 'name', 'Station 2')
    setattr(stations[2], 'name', 'Bad Station')

    # all should run without exception
    plot_water_level_with_polyfit(stations[0], dates['Station 1'], levels['Station 1'], 4)
    plot_water_level_with_polyfit(stations[1], dates['Station 2'], levels['Station 2'], 4)
    plot_water_level_with_polyfit(stations[2], dates['Bad Station'], levels['Bad Station'], 4)

    plot_water_level_with_polyfit(stations[0], dates['Station 1'], levels['Station 1'], 4, format_dates=True)
    plot_water_level_with_polyfit(stations[0], dates['Station 1'], levels['Station 1'], 4, y_axis_from_zero=False)
    plot_water_level_with_polyfit(stations[0], dates['Station 1'], levels['Station 1'], 4, use_proplot_style=False)
