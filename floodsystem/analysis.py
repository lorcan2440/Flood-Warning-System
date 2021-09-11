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


def identify_potentially_bad_data(station_name: str, levels: list[float], **kwargs: dict) -> set:

    NEGATIVE_LEVEL_TO_ZERO      = kwargs.get('negative_level_to_zero',      True)   # noqa
    REPLACE_TUPLE_WITH_INDEX    = kwargs.get('replace_tuple_with_index',    1)      # noqa
    TOO_HIGH_CUTOFF             = kwargs.get('too_high_cutoff',             2500)   # noqa
    TOO_HIGH_TO_PREVIOUS_LEVEL  = kwargs.get('too_high_to_previous_level',  True)   # noqa

    IS_TIDAL        = getattr(kwargs.get('station_obj', None), 'is_tidal', False)   # noqa

    flags = set()

    for i in range(len(levels)):

        # Check for erroneous case: level was a tuple instead of float
        if not isinstance(levels[i], (float, int)):

            warn_str = f"Data for {station_name} station on date may be unreliable. "
            warn_str += f"Found water level value {levels[i]}. \n"
            warn_str += f"This has been replaced with {levels[i][REPLACE_TUPLE_WITH_INDEX]}."

            flags.add(warn_str)

            levels[i] = levels[i][REPLACE_TUPLE_WITH_INDEX]

        # Check for potentially invalid values: negative or impossibly high
        if levels[i] < 0 and not IS_TIDAL:

            warn_str = f"Data for {station_name} station may be unreliable. "
            warn_str += "Some water levels were found to be negative, \nand this station is not tidal. "
            warn_str += "These have been set to 0 m."

            flags.add(warn_str)

            if NEGATIVE_LEVEL_TO_ZERO:
                levels[i] = 0

        if levels[i] > TOO_HIGH_CUTOFF and len(levels) >= 2:

            warn_str = f"Data for {station_name} station may be unreliable. "
            warn_str += "Some water levels were found to be very high, above "
            warn_str += f"{TOO_HIGH_CUTOFF} m. \nThese have been set to whatever "
            warn_str += "the value before the spike."

            flags.add(warn_str)

            if TOO_HIGH_TO_PREVIOUS_LEVEL:
                levels[i] = levels[i - 1]

    # Check for potentially invalid values: many sudden changes
    if has_rapid_fluctuations(levels, is_tidal=IS_TIDAL):

        warn_str = f"Data for {station_name} station may be unreliable. "
        warn_str += "There are many sudden spikes between consecutive measurements. "
        warn_str += "These values have not been altered."

        flags.add(warn_str)

    return flags


def has_rapid_fluctuations(levels: list[float], is_tidal: bool = False, stdev_tol: float = 0.05) -> bool:

    # TODO: try an AI based approach? This is not perfect
    # currently flags if standard deviation in stepwise changes is more than 5% of the average value.

    diffs = [levels[i + 1] - levels[i] for i in range(len(levels) - 1)]
    average_val = np.average(levels)
    stdev = np.std(diffs)

    # allow much more variation if tidal (daily spikes are natural)
    if is_tidal:
        stdev_tol *= 10

    return stdev / average_val > stdev_tol
