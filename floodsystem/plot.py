"""
This module provides graphing functionality
for visualising level data over time.
"""

# built-in libraries
import math
import os
import datetime

# third-party libraries
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.dates import DateFormatter

# local imports
try:
    from .utils import flatten
    from .analysis import polyfit, moving_average
    from .station import MonitoringStation
except ImportError:
    from utils import flatten
    from analysis import polyfit, moving_average
    from station import MonitoringStation


RESOURCES = os.path.join(os.path.dirname(__file__), 'assets')
PROPLOT_STYLE_SHEET = os.path.join(RESOURCES, 'proplot_style.mplstyle')


def plot_water_levels(stations: list, dates: dict, levels: dict, as_subplots: bool = True,
                      use_proplot_style: bool = True, subplots_share_y_axis: bool = False):
    '''
    Plots graph(s) of the level data in stations (which may be a single
    MonitoringStation object or a list of them).

    #### Arguments

    `stations` (list): list of input stations
    `dates` (dict): dates where data is available
    `levels` (dict): level data corresponding to the given dates
    `as_subplots` (bool, default = True): whether to use multiple plots on the same figure
    `use_proplot_style` (bool, default = True): use ProPlot stylesheet
    `subplots_share_y_axis` (bool, default = False): if using subplots, all y-axes share same limits
    '''

    # remove all stations with inconsistent typical range
    for s in stations:
        if not s.typical_range_consistent():
            levels.pop(s.name, None)
            dates.pop(s.name, None)
            stations.remove(s)

    assert len(list(levels.keys())) == len(stations)

    if use_proplot_style:
        plt.style.use(PROPLOT_STYLE_SHEET)
    else:
        plt.style.use('default')

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
            axs[0][i].set_ylim(0, 1.3 * max(list(levels.values())[i]))

        for i in range(y - (len(stations) % 2)):
            axs[1][i].plot(list(dates.values())[i + y], list(levels.values())[i + y])
            axs[1][i].set_title(stations[i + y].name)
            axs[1][i].set_xlabel('dates')
            axs[1][i].set_ylabel('water level / $ m $')
            axs[1][i].tick_params(axis='x', rotation=30)
            axs[1][i].set_ylim(0, 1.3 * max(list(levels.values())[i + y]))

        if subplots_share_y_axis:
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


def plot_water_level_with_polyfit(station: MonitoringStation, dates: list, levels: list,
        poly_degree: int = 5, n_points: int = 100, format_dates: bool = True,
        y_axis_from_zero: bool = None, use_proplot_style: bool = True):
    '''
    Plot water level data with a polynomial least-squares best-fit curve.

    #### Arguments

    `station` (MonitoringStation): list of input stations
    `dates` (list): dates where data is available
    `levels` (list): level data corresponding to the given dates
    `poly_degree` (int, default = 5): degree of polynomial fit
    `n_points` (int, default = 100): number of points to sample the polynomial curve
    `format_dates` (bool, default = True): format dates neater
    `y_axis_from_zero` (bool, default = None): whether to start the y-axis from the zero level
    `use_proplot_style` (bool, default = True): use ProPlot stylesheet
    '''

    if use_proplot_style:
        plt.style.use(PROPLOT_STYLE_SHEET)
    else:
        plt.style.use('default')

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
        format_dates: bool = True, y_axis_from_zero: bool = None, use_proplot_style: bool = True):
    '''
    Plot water level data with a symmetric moving average curve.

    #### Arguments

    `station` (MonitoringStation): list of input stations
    `dates` (list): dates where data is available
    `levels` (list): level data corresponding to the given dates
    `interval` (int, default = 3): window size for moving average
    `format_dates` (bool, default = True): format dates neater
    `y_axis_from_zero` (bool, default = None): whether to start the y-axis from the zero level
    `use_proplot_style` (bool, default = True): use ProPlot stylesheet
    '''

    if use_proplot_style:
        plt.style.use(PROPLOT_STYLE_SHEET)
    else:
        plt.style.use('default')

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


def plot_predicted_water_levels(station: MonitoringStation, dates_future: list[datetime.datetime],
        levels_future_predicted: list[float], format_dates: bool = True, y_axis_from_zero: bool = None,
        use_proplot_style: bool = True, **kwargs):
    '''
    Plots the forecast of a station, including past predictions.

    #### Arguments

    `station` (MonitoringStation): the station which has the forecast to be plotted
    `dates_future` (list[datetime.datetime]): the dates into the future where a forecast is given
    `levels_future_predicted` (list[float]): the forecasted levels

    #### Optional Keywords Arguments

    `format_dates` (bool, default = True): format dates neater
    `y_axis_from_zero` (bool, default = None): whether to start the y-axis from the zero level
    `use_proplot_style` (bool, default = True): use ProPlot stylesheet
    `dates_to_now` (list, default = None): the dates where a past forecast exist
    `levels_to_now` (list, default = None): the true levels over the dates_to_now
    `levels_past_predicted` (list, default = None): the levels predicted by a past forecast
    `metadata` (dict, default = None): additional info about the forecast, including about the model used.
        {'has_past_forecast', 'dataset_size', 'lookback', 'iterations', 'batch_size', 'used_pretrained', 'epochs'}'''   # noqa

    dates_to_now = kwargs.get('dates_to_now', None)
    levels_to_now = kwargs.get('levels_to_now', None)
    levels_past_predicted = kwargs.get('levels_past_predicted', None)
    _metadata = kwargs.get('metadata', None)
    station_name = station.name

    if _metadata is not None:
        has_past_forecast = _metadata['has_past_forecast']
    else:
        has_past_forecast = all([i is not None for i in [dates_to_now, levels_to_now, levels_past_predicted]])

    if use_proplot_style:
        plt.style.use(PROPLOT_STYLE_SHEET)
    else:
        plt.style.use('default')

    if y_axis_from_zero is None:
        y_axis_from_zero = not station.is_tidal

    if has_past_forecast:
        plt.plot(dates_to_now, levels_to_now,
            label='Past levels', color='#000000')
        plt.plot(dates_to_now, levels_past_predicted,
            label='Past forecast', color='#29a762', linestyle='dashed')

    plt.plot(dates_future, levels_future_predicted, label='Forecast', color='#c12091', linestyle='dashed')

    if station.typical_range_consistent():
        plt.fill_between(
            [dates_to_now[0], dates_future[-1]] if has_past_forecast else [dates_future[0], dates_future[-1]],
            station.typical_range[0], station.typical_range[1], facecolor='green', alpha=0.2,
            label=f'Typical range: \n{station.typical_range[0]} - {station.typical_range[1]}')

    # graphical - main figure
    plt.xlabel('date')
    plt.ylabel('water level / $ m $')
    plt.legend(loc='upper left')
    plt.title('Water levels and forecast ' +    # noqa
        f'{"for " + station_name if station_name is not None else "(station unspecified)"}')
    plt.xticks(rotation=45)
    plt.tight_layout()
    if y_axis_from_zero:
        plt.ylim(ymin=0)

    # graphical - axes
    ax = plt.gca()
    if format_dates:  # string date formats: https://strftime.org/
        ax.xaxis.set_major_formatter(DateFormatter('%d %b, %I:%M %p'))

    plt.show()


def plot_model_loss(history: list, loss_name: str, model_name: str, use_logscale: bool = True,
        use_proplot_style: bool = True, batch_size: int = None, show_colors: bool = True):
    '''
    Shows a graph of the convergence of the loss for each epoch for a trained model.
    Called by `floodsystem.forecasts.train_model`.

    #### Arguments

    `history` (list): values of losses to be plotted
    `loss_name` (str): name of loss function used when training model
    `model_name` (str): name of the station which this model is based on

    #### Optional

    `use_logscale` (bool, default = True): whether to show loss on a vertical log axis
    `use_proplot_style` (bool, default = True): use ProPlot stylesheet
    `batch_size` (int, default = None): batch size used when training model. Shows 'unspecified' if None.
    `show_colors` (bool, default = True): indicate quality based on loss with colours.
        Only shows when using mse loss (`loss_name == 'Mean Squared Error'`)
    '''

    if batch_size is None:
        batch_size = 'unspecified'

    epoch = len(history)
    end_loss = history[-1]

    if use_proplot_style:
        plt.style.use(PROPLOT_STYLE_SHEET)
    else:
        plt.style.use('default')

    if show_colors and loss_name == 'Mean Squared Error':
        GREEN = '#18b83d'
        YELLOW = '#e3b51e'
        RED = '#b81818'
        plt.fill_between([1, epoch], 1e-5, 1e-3, facecolor=GREEN, alpha=0.4)
        plt.fill_between([1, epoch], 1e-3, 1e-2, facecolor=YELLOW, alpha=0.4)
        plt.fill_between([1, epoch], 1e-2, 2e-0, facecolor=RED, alpha=0.4)
        loss_color = GREEN if end_loss < 1e-3 else YELLOW if end_loss < 1e-2 else RED
    else:
        loss_color = None

    plt.title(f'Loss convergence of training for {model_name}')
    plt.plot(np.arange(1, epoch + 1), history, label='loss',
        color='#999999', linestyle='dotted', marker='x', markeredgecolor='#000000')
    plt.hlines(end_loss, 1, epoch, colors=loss_color, linestyles='dashed',
        label=f'converged on {round(end_loss, 6)}', zorder=-1)

    plt.xticks(range(epoch + 1))
    plt.xlim(left=1, right=epoch)
    plt.ylim(bottom=7e-5, top=1.5e-0)
    plt.legend()
    plt.xlabel(f'Epoch number (batch size {batch_size}), out of {epoch}')
    plt.ylabel(f'Loss ({loss_name})')
    if use_logscale:
        plt.yscale('log')

    plt.show()
