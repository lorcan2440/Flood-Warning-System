'''
This module provides functions for fitting
least-squares regression curves to water
level data.
'''

import datetime
import numpy as np
from matplotlib.dates import date2num


def polyfit(dates: list[datetime.datetime],
            levels: list[float], p: int) -> tuple[np.poly1d, float, list[float]]:

    '''
    Returns a tuple of a p-degree polynomial
    (numpy.poly1d object), an x-axis offset,
    and the original data as a list of floats.

    Inputs:

    dates, a list of the dates at which to plot
    (a list of datetime.datetime objects);
    levels, a list of the water levels at each corresponding date
    (a list of floats);
    p, the degree of the polynomial to approximate with
    (an int)

    Output:

    (poly, time_shift, date_nums); where
    poly is a callable np.poly1d function representing the polynomial;
    time_shift is a float, a fixed offset;
    date_nums is a list of floats, representing the original dates as floats.
    '''

    # standard data type and bounds input checks
    assert len(dates) == len(levels)
    assert all([isinstance(d, datetime.datetime) for d in dates])
    assert all([isinstance(lev, (float, int)) for lev in levels])
    assert isinstance(p, int) and 0 <= p <= len(dates) - 1

    # convert datetime objects to floats
    date_nums = date2num(dates)

    # to minimise the size of the numbers inputted to np.polyfit,
    # offset it by the mean of the dataset
    time_shift = np.mean(date_nums)
    p_coeff = np.polyfit(date_nums - time_shift * np.ones(len(date_nums)), levels, p)

    # convert to a callable polynomial function
    poly = np.poly1d(p_coeff)

    # return the polynomial, the shift and the input data (as floats)
    return (poly, time_shift, date_nums)


def moving_average(dates: list[datetime.datetime], levels: list[float], interval: int = 3):

    date_nums = date2num(dates)

    # find the moving average, ignoring the ends
    lma = np.convolve(levels, np.ones(interval), mode='valid') / interval

    if interval % 2 == 1:
        # odd number of points: append original values to either end
        half_end = interval // 2
        lma = np.insert(lma, 0, levels[:half_end])
        lma = np.insert(lma, len(lma), levels[-1 * half_end:])
        return date_nums, lma

    else:
        # even number of points: append moving averages of the missing intervals to either end,
        # and move date values over by half an interval to account for this
        half_end = round((interval / 2) - 1)
        lma = np.insert(lma, 0, np.convolve(levels[:half_end + 1], (0.5, 0.5), mode='valid'))
        lma = np.insert(lma, len(lma), np.convolve(levels[-1 * half_end - 1:], (0.5, 0.5), mode='valid'))
        date_interval = date_nums[1] - date_nums[0]
        date_nums = [dn + date_interval / 2 for dn in date_nums]
        date_nums.pop()
        return date_nums, lma


def has_rapid_fluctuations(levels: list[float], stdev_tol: float = 0.05) -> bool:

    # TODO: try an AI based approach? This is not perfect

    diffs = [levels[i + 1] - levels[i] for i in range(len(levels) - 1)]
    average_val = np.average(levels)
    stdev = np.std(diffs)

    return stdev / average_val > stdev_tol
