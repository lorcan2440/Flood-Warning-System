'''
Unit tests for the analysis module.
'''

# pylint: disable=import-error

import import_helper  # noqa
from datetime import datetime as dt
from matplotlib.dates import date2num
import numpy as np

from floodsystem.analysis import polyfit


def test_polyfit():

    dates = [dt(2020, 1, 1), dt(2020, 1, 2), dt(2020, 1, 3), dt(2020, 1, 4)]
    levels = [20, 25, 23, 28]
    TEST_P = 3

    poly, time_shift, date_nums = polyfit(dates, levels, TEST_P)

    assert isinstance(poly, np.poly1d)
    assert 20 <= poly(date2num(dt(2020, 1, 2, 12)) - time_shift) <= 28
    assert time_shift > date2num(dt(2020, 1, 1))
    assert len(date_nums) == len(dates)
