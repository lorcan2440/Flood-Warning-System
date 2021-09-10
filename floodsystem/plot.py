"""
This module provides graphing functionality
for visualising level data over time.
"""

# pylint: disable=relative-beyond-top-level

from floodsystem.station import MonitoringStation
import math
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.dates import DateFormatter

from .utils import flatten
from .analysis import polyfit, moving_average


def plot_water_levels(stations: list, dates: dict, levels: dict, as_subplots: bool = True,
                      use_proplot_style: bool = True) -> None:

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

    # remove all stations with inconsistent typical range
    for s in stations:
        if not s.typical_range_consistent():
            levels.pop(s.name, None)
            dates.pop(s.name, None)
            stations.remove(s)

    assert len(list(levels.keys())) == len(stations)

    if use_proplot_style:
        plt.style.use('proplot_style.mplstyle')

    if as_subplots:

        y = math.ceil(len(stations) / 2)
        x = round(len(stations) / y)

        fig, axs = plt.subplots(x, y, figsize=(12, 6))

        for i in range(y):
            axs[0][i].plot(list(dates.values())[i], list(levels.values())[i])
            axs[0][i].set_title(stations[i].name)
            axs[0][i].set_xlabel('dates')
            axs[0][i].set_ylabel('water level / $ m $')
            axs[0][i].tick_params(axis='x', rotation=30)

        for i in range(y - (len(stations) % 2)):
            axs[1][i].plot(list(dates.values())[i + y], list(levels.values())[i + y])
            axs[1][i].set_title(stations[i + y].name)
            axs[1][i].set_xlabel('dates')
            axs[1][i].set_ylabel('water level / $ m $')
            axs[1][i].tick_params(axis='x', rotation=30)

        plt.setp(axs, ylim=(0, 0.5 + max(flatten(list(levels.values())))))
        fig.tight_layout()
        fig.show()

    else:

        for s in stations:
            plt.plot(dates[s.name], levels[s.name], label=s.name)

        plt.ylim(ymin=0)
        plt.title('Recorded water levels')
        plt.xlabel('date')
        plt.ylabel('water level / $ m $')
        plt.xticks(rotation=45)
        plt.legend(loc='upper left')
        plt.tight_layout()

    plt.show()


def plot_water_level_with_polyfit(station: object, dates: list, levels: list, poly_degree: int = 5,
        n_points: int = 100, format_dates: bool = True, y_axis_from_zero: bool = None,
        use_proplot_style: bool = True) -> None:

    if use_proplot_style:
        plt.style.use('proplot_style.mplstyle')

    if y_axis_from_zero is None:
        y_axis_from_zero = not station.is_tidal

    # Get a polynomial function fitting the data, the offset, and the original dataset.
    poly, d0, date_nums = polyfit(dates, levels, poly_degree)

    # plot given data
    plt.plot(dates, levels, '.', label=station.name)

    # sample from the data and plot with the offset
    x1 = np.linspace(date_nums[0], date_nums[-1], n_points)
    plt.plot(x1, poly(x1 - d0), label='Best-fit curve')

    # plot the typical range as a shaded region
    if station.typical_range_consistent():
        plt.fill_between([x1[0], x1[-1]], station.typical_range[0], station.typical_range[1],
        facecolor='green', alpha=0.2,
        label=f'Typical range: \n{station.typical_range[0]}-{station.typical_range[1]}')
    else:
        plt.plot(date_nums[-1], levels[-1], label='(typical range' + '\n' + 'unavailable)')

    # graphical - main figure
    plt.xlabel('date')
    plt.ylabel('water level / $ m $')
    plt.legend(loc='upper left')
    plt.xticks(rotation=45)
    plt.tight_layout()
    if y_axis_from_zero:
        plt.ylim(ymin=0)

    # graphical - axes
    ax = plt.gca()
    if format_dates:  # string date formats: https://strftime.org/
        ax.xaxis.set_major_formatter(DateFormatter('%d %b, %I:%M %p'))

    plt.show()


def plot_water_level_with_moving_average(station: object, dates: list, levels: list, interval: int = 3,
        format_dates: bool = True, y_axis_from_zero: bool = None, use_proplot_style: bool = True) -> None:

    if use_proplot_style:
        plt.style.use('proplot_style.mplstyle')

    if y_axis_from_zero is None:
        y_axis_from_zero = not station.is_tidal

    # Get average data
    date_nums, avg_levels = moving_average(dates, levels, interval)

    # plot given and moving average data
    plt.plot(dates, levels, '.', label=station.name)
    plt.plot(date_nums, avg_levels, label=f'{interval}-point SMA')

    # plot the typical range as a shaded region
    if station.typical_range_consistent():
        plt.fill_between([dates[0], dates[-1]], station.typical_range[0], station.typical_range[1],
                         facecolor='green', alpha=0.2,
                         label=f'Typical range: \n{station.typical_range[0]}-{station.typical_range[1]}')
    else:
        plt.plot(date_nums[-1], levels[-1], label='(typical range' + '\n' + 'unavailable)')

    # graphical - main figure
    plt.xlabel('date')
    plt.ylabel('water level / $ m $')
    plt.legend(loc='upper left')
    plt.xticks(rotation=45)
    plt.tight_layout()
    if y_axis_from_zero:
        plt.ylim(ymin=0)

    # graphical - axes
    ax = plt.gca()
    if format_dates:  # string date formats: https://strftime.org/
        ax.xaxis.set_major_formatter(DateFormatter('%d %b, %I:%M %p'))

    plt.show()


def plot_predicted_water_levels(station: MonitoringStation, dates, levels,
        format_dates: bool = True, y_axis_from_zero: bool = None, use_proplot_style: bool = True):

    if use_proplot_style:
        plt.style.use('proplot_style.mplstyle')

    if y_axis_from_zero is None:
        y_axis_from_zero = not station.is_tidal

    plt.plot(dates[0], levels[0], label='Past levels', color='#000000')
    plt.plot(dates[0], levels[1], label='Demo levels', color='#29a762', linestyle='dashed')
    plt.plot(dates[1], levels[2], label='Forecast', color='#c12091', linestyle='dashed')

    if station.typical_range_consistent():
        plt.fill_between([dates[0][0], dates[1][-1]], station.typical_range[0], station.typical_range[1],
            facecolor='green', alpha=0.2,
            label=f'Typical range: \n{station.typical_range[0]}-{station.typical_range[1]}')
    else:
        plt.plot(dates[0][-1], levels[0][-1], label='(typical range' + '\n' + 'unavailable)')

    # graphical - main figure
    plt.xlabel('date')
    plt.ylabel('water level / $ m $')
    plt.legend(loc='upper left')
    plt.title(f'Water levels and forecast for {station.name}')
    plt.xticks(rotation=45)
    plt.tight_layout()
    if y_axis_from_zero:
        plt.ylim(ymin=0)

    # graphical - axes
    ax = plt.gca()
    if format_dates:  # string date formats: https://strftime.org/
        ax.xaxis.set_major_formatter(DateFormatter('%d %b, %I:%M %p'))

    plt.show()
