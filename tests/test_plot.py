'''
Unit tests for the plot module.
'''

# pylint: disable=import-error

import import_helper  # noqa
import pytest
from datetime import datetime

from floodsystem.plot import plot_water_level_with_moving_average, plot_water_levels, \
    plot_water_level_with_polyfit


@pytest.mark.parametrize("kwargs",
    [{}, {'as_subplots': False}, {'use_proplot_style': False},
    {'as_subplots': False, 'use_proplot_style': False}])
def test_plot_water_levels(create_dates_and_levels, kwargs):

    plot_water_levels(*create_dates_and_levels, **kwargs)


@pytest.mark.parametrize("index, name, degree, kwargs",
    [(0, 'Station 1', 4, {}), (1, 'Station 2', 3, {}), (3, 'Bad Station', 4, {}),
    (0, 'Station 1', 4, {'format_dates': False}), (1, 'Station 2', 5, {'y_axis_from_zero': False}),
    (2, 'Station 3', 3, {'use_proplot_style': False})])
def test_plot_water_level_with_fit(create_dates_and_levels, index, name, degree, kwargs):

    stations, dates, levels = create_dates_and_levels

    plot_water_level_with_polyfit(stations[index], dates[name], levels[name], poly_degree=degree, **kwargs)
    plot_water_level_with_moving_average(stations[index], dates[name], levels[name], interval=degree, **kwargs)
