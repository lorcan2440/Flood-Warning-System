'''
This module provides functions for fitting
least-squares regression curves to water
level data.
'''

import datetime

import numpy as np
from matplotlib.dates import date2num


def polyfit(dates: list[datetime.datetime], levels: list[float],
        p: int = 3) -> tuple[np.poly1d, float, list[float]]:
    '''
    Finds a polynomial best-fit (least squares) curve to a given dataset.

    #### Arguments

    `dates` (list[datetime.datetime]): a list of dates where there is level data
    `levels` (list[float]): a list of level data points to fit
    `p` (int, default = 3): the degree of the polynomial curve to use

    #### Returns

    tuple[np.poly1d, float, list[float]]: the callable polynomial function, the constant
    offset used to shift the dates from their mean, and the original dates as numbers, respectively

    #### Raises

    `TypeError`: if inputs are not the specified type(s)
    `ValueError`: if degree is not integer
    '''

    # standard data type and bounds input checks
    if len(dates) != len(levels):
        raise ValueError(f'Inputs must be same length; sizes are {len(dates)} and {len(levels)}')
    if not all([isinstance(d, datetime.datetime) for d in dates]):
        raise TypeError('All dates must be datetime.datetime instances.')
    if not all([isinstance(lev, (float, int)) for lev in levels]):
        raise TypeError('All levels must be numbers.')
    if not (isinstance(p, int) and 0 <= p <= len(dates) - 1):
        raise ValueError('Polynomial degree must be integer, positive and less than the input length.')

    # convert datetime objects to floats
    date_nums = date2num(dates)

    # to minimise the size of the numbers inputted to np.polyfit, offset it by the mean of the dataset
    time_shift = np.mean(date_nums)
    p_coeff = np.polyfit(date_nums - time_shift * np.ones(len(date_nums)), levels, p)

    # convert to a callable polynomial function
    poly = np.poly1d(p_coeff)

    # return the polynomial, the shift and the input data (as floats)
    return (poly, time_shift, date_nums)


def moving_average(dates: list[datetime.datetime], levels: list[float],
        interval: int = 3) -> tuple[list[float], np.ndarray]:
    '''
    Calculates a moving average of the given data, extending the domain to use
    smaller intervals at the endpoints. If the interval is odd, the output domain
    will be the same; if the interval is even, the output domain will be at the
    midpoints of the original.

    #### Arguments

    `dates` (list[datetime.datetime]): list of dates where there is level data
    `levels` (list[float]): list of levels to be averaged
    `interval` (int, default = 3): symmetric window size over which to average

    #### Returns

    tuple[list[float], np.ndarray]: the new domain and averaged values at these points, respectively

    #### Raises

    `ValueError`: if interval is not between 1 and the input length
    '''

    if not (isinstance(interval, int) and 1 <= interval <= len(dates)):
        raise ValueError('Interval size must between 1 and the input length')

    date_nums = date2num(dates)

    # find the moving average, ignoring the ends
    averages = np.convolve(levels, np.ones(interval), mode='valid') / interval

    if interval % 2 == 1:
        # odd number of points: append original values to either end
        half_end = interval // 2
        averages = np.insert(averages, 0, levels[:half_end])
        averages = np.insert(averages, len(averages), levels[-1 * half_end:])
        return date_nums, averages

    else:
        # even number of points: append moving averages of the missing intervals to either end,
        # and move date values over by half an interval to account for this
        half_end = round((interval / 2) - 1)
        averages = np.insert(averages, 0, np.convolve(levels[:half_end + 1], (0.5, 0.5), mode='valid'))
        averages = np.insert(averages, len(averages),
            np.convolve(levels[-1 * half_end - 1:], (0.5, 0.5), mode='valid'))
        date_interval = date_nums[1] - date_nums[0]
        date_nums = [dn + date_interval / 2 for dn in date_nums]
        date_nums.pop()
        return date_nums, averages


def identify_potentially_bad_data(station_name: str, levels: list[float],
        data_origin_type: str = None, **kwargs: dict) -> set[str]:
    '''
    Check for suspicious values within a station's water level records. Tests for:

    1. If a level is given as a tuple instead of a float
    2. If negative (when not a tidal station) or extremely large values
    3. If the level fluctuates significantly between readings

    and returns appropriate warning messages or an empty set if there are none.

    #### Arguments

    `station_name` (str): string name of a station to be displayed. Does not have to be the official name.
    `levels` (list[float]): list of level data to be checked
    `data_origin_type` (str, default = None): either 'RIVER_STATION', 'RAINFALL_GAUGE' or unspecified (None)

    #### Returns

    set[str]: a set of string messages detailing the potential errors in the data.
    '''

    NEGATIVE_LEVEL_TO_ZERO      = kwargs.get('negative_level_to_zero',      True)   # noqa
    REPLACE_TUPLE_WITH_INDEX    = kwargs.get('replace_tuple_with_index',    1)      # noqa
    TOO_HIGH_CUTOFF             = kwargs.get('too_high_cutoff',             2500)   # noqa
    TOO_HIGH_TO_PREVIOUS_LEVEL  = kwargs.get('too_high_to_previous_level',  True)   # noqa

    IS_TIDAL        = getattr(kwargs.get('station_obj', None), 'is_tidal', False)   # noqa

    flags = set()

    for i in range(len(levels)):

        # Check for erroneous case: level was a tuple instead of float
        if not isinstance(levels[i], (float, int)):

            if isinstance(correct_level := levels[i][REPLACE_TUPLE_WITH_INDEX], (float, int)):
                warn_str = f"Data for {station_name} station on date may be unreliable. "
                warn_str += f"Found water level value {levels[i]}. \n"
                warn_str += f"This has been replaced with {correct_level}."
                flags.add(warn_str)
                levels[i] = correct_level
            else:
                warn_str = f"Data for {station_name} station on date may be unreliable. "
                warn_str += f"Found water level value {levels[i]}. This item was \n"
                warn_str += "unable to be resolved into a numerical value, and has not been altered."
                flags.add(warn_str)

        # Check for potentially invalid values: negative or impossibly high
        if levels[i] < 0 and not IS_TIDAL:

            warn_str = f"Data for {station_name} station may be unreliable. "
            warn_str += "Some water levels were found to be negative, \nand this station is not tidal. "
            if NEGATIVE_LEVEL_TO_ZERO:
                warn_str += "These have been set to 0 m."
                levels[i] = 0

            flags.add(warn_str)

        if levels[i] > TOO_HIGH_CUTOFF and len(levels) >= 2:

            warn_str = f"Data for {station_name} station may be unreliable. "
            warn_str += f"Some water levels were found to be very high, above {TOO_HIGH_CUTOFF} m.\n"
            if TOO_HIGH_TO_PREVIOUS_LEVEL:
                warn_str += "These have been set to whatever the value before the spike."
                levels[i] = levels[i - 1]

            flags.add(warn_str)

    # Check for potentially invalid values: many sudden changes
    if data_origin_type == 'RIVER_STATION':
        if has_rapid_fluctuations(levels):

            warn_str = f"Data for {station_name} station may be unreliable. "
            warn_str += "There are many sudden spikes between consecutive measurements. \n"
            warn_str += "These values have not been altered."

            flags.add(warn_str)

    return flags


def has_rapid_fluctuations(levels: list[float], interval: int = 3, tol: float = 5e-3) -> bool:
    '''
    Applies a simple statistical estimate to check whether a
    dataset has rapid changes between values. Aims to allow daily
    cycles which are natural for tidal stations.

    The test applied is: mean squared error of the levels relative
    to the moving (interval-specified) average must be less than a
    (tol-specified) fraction of the squared mean level.

    #### Arguments

    `levels` (list[float]): list of level data to analyse
    `interval` (int, default = 3): the interval of the moving average used in the computation
    `tol` (float, default = 5e-3): the relative tolerance when compared to the mean square level

    #### Returns

    bool: True if there are rapid fluctuations detected; False otherwise
    '''

    import numpy as np

    lv = np.array(levels)
    _, avg = moving_average(*zip(*enumerate(levels)), interval)
    mse = ((lv - avg) ** 2).mean()

    return mse / (lv.mean() ** 2) >= tol
