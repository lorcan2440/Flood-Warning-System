"""
This module provides graphing functionality
for visualising level data over time.
"""

# pylint: disable=relative-beyond-top-level

import datetime
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.dates import num2date

from .station import MonitoringStation
from .utils import flatten
from .analysis import polyfit


def plot_water_levels(stations: list, dates: dict, levels: dict):

    '''
    Plots graph(s) of the level data in stations (which may be
    a single MonitoringStation object or a list of them).

    Inputs:

    stations, the stations to analyse
    (a list of MonitoringStation objects);
    dates, the dates at which to plot
    (a dict, mapping the MonitoringStation.name to a list of datetime.datetime objects);
    levels, the data corresponding to each date
    (a dict, mapping the MonitoringStation.name to a list of floats).
    '''

    # Standard data type input checks
    assert isinstance(stations, list)
    assert isinstance(dates, dict)
    assert isinstance(levels, dict)
    assert all([isinstance(i, MonitoringStation) for i in stations])
    assert all([isinstance(i, datetime.datetime) for i in flatten(list(dates.values()))])
    assert all([isinstance(i, (float, int)) for i in flatten(list(levels.values()))])

    # Discard any stations with bad range, dates or levels data
    stations, dates, levels = stations, dates, levels

    for s in stations:
        if not s.typical_range_consistent():
            levels.pop(s.name, None)
            dates.pop(s.name, None)
            stations.remove(s)

    # After removals, check sizes of lists are valid
    assert len(list(levels.keys())) == len(stations)

    for s in stations:
        plt.plot(dates[s.name], levels[s.name], label=s.name)

    plt.xlabel('date')
    plt.ylabel('water level / $ m $')
    plt.xticks(rotation=45)
    plt.legend(loc='upper right')
    plt.tight_layout()
    plt.show()


def plot_water_level_with_fit(station: object, dates: list, levels: list, p: int,
        n_points: int = 30, format_dates: bool = False):

    # Get a polynomial function fitting the data, the offset, and the original dataset.
    poly, d0, date_nums = polyfit(dates, levels, p)

    # If the time axis should be displayed using nice dates,
    # plot the data as floats initially, which is later
    # labelled as formatted datetime.datetime strings
    # or datetime.datetime objects if not
    if format_dates:
        plt.plot(date_nums, levels, '.', label=station.name)
        date_nums_sample = np.linspace(date_nums[0], date_nums[-1], 12)
        dates_formatted = [d.strftime('%b %d, %I %p') for d in num2date(date_nums_sample)]
        plt.xticks(date_nums_sample, labels=dates_formatted, rotation=45)
    else:
        plt.plot(num2date(date_nums), levels, '.', label=station.name)
        plt.xticks(rotation=45)

    # sample from the data and plot with the offset
    x1 = np.linspace(date_nums[0], date_nums[-1], n_points)
    plt.plot(x1, poly(x1 - d0), label='Best-fit curve')

    # plot the typical range as a shaded region
    if station.typical_range_consistent():
        plt.fill_between(x1, station.typical_range[0] * np.ones(len(x1)),
            station.typical_range[1] * np.ones(len(x1)), facecolor='green', alpha=0.2,
            label=f'Typical range: \n{station.typical_range[0]}-{station.typical_range[1]}')
    else:
        plt.plot(date_nums[-1], levels[-1], label='(typical range' + '\n' + 'unavailable)')

    # graphical
    plt.xlabel('date')
    plt.ylabel('water level / $ m $')
    plt.legend(loc='upper right')
    plt.tight_layout()
    plt.show()
