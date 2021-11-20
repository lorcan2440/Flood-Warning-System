# pylint: disable=import-error

import import_helper  # noqa

from datetime import datetime
import pytest

from floodsystem.station import MonitoringStation


@pytest.fixture()
def create_dates_and_levels():

    stations = [
        MonitoringStation(None, 'Station 1', None, (10, 20)),
        MonitoringStation(None, 'Station 2', None, (5, 15)),
        MonitoringStation(None, 'Station 3', None, (6, 7)),
        MonitoringStation(None, 'Bad Station', None, None)
    ]

    # a mixture of different amounts of dates, invalid dates and bad formats
    dates = {'Station 1':
        [datetime(2016, 12, 30), datetime(2017, 1, 1),
        datetime(2017, 1, 2), datetime(2017, 1, 3), datetime(2017, 1, 4), datetime(2017, 1, 5)],
        'Station 2':
        [datetime(2016, 12, 30), datetime(2016, 12, 31), datetime(2017, 1, 1),
        datetime(2017, 1, 2), datetime(2017, 1, 3), datetime(2017, 1, 4), datetime(2017, 1, 5)],
        'Station 3':
        [datetime(2016, 12, 30), datetime(2017, 1, 1),
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

    return stations, dates, levels
