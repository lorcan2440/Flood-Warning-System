"""
This module provides graphing functionality
for visualising level data over time.
"""

import datetime

from .station import MonitoringStation
from .utils import flatten
from matplotlib import pyplot as plt


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
