'''
Unit tests for the station_data module.
'''

# pylint: disable=import-error

import datetime
import time
import os
import shutil
import import_helper  # noqa

from floodsystem.datafetcher import fetch, dump, load, \
    fetch_measure_levels, fetch_latest_water_level_data, fetch_station_data
from floodsystem.station_data import build_station_list


# get data from url first and reuse in each test to avoid excessive calls
TEST_URL = "http://environment.data.gov.uk/flood-monitoring/id/stations?status=Active&parameter=level&qualifier=Stage&_view=full"  # noqa
response = fetch(TEST_URL)

# give permissions to delete a cache folder
os.chmod('cache', 0o777)
time.sleep(0.1)  # include pauses before each non-cached call to prevent getting blocked out


def test_fetch():

    assert response is not None
    assert len(response['items']) > 0
    assert len(list(filter(lambda s: s['riverName'] == 'River Cam' and s['town'] == 'Cam',
        response['items']))) == 1


def test_dump():

    assert response is not None
    dump(response, 'test_dump.json')
    assert os.path.isfile('test_dump.json')
    os.remove('test_dump.json')
    assert not os.path.isfile('test_dump.json')


def test_load():

    dump(response, 'test_load.json')
    json_dict_loaded = load('test_load.json')
    assert response == json_dict_loaded
    assert json_dict_loaded is not None


def test_fetch_station_data():

    # try using cache when it doesn't exist
    shutil.rmtree('cache')
    test_fetch = fetch_station_data(use_cache=True)
    assert test_fetch is not None

    # cache exists, use and don't use
    test_fetch = fetch_station_data(use_cache=True)
    assert test_fetch is not None
    time.sleep(0.1)
    test_fetch = fetch_station_data(use_cache=False)
    assert test_fetch is not None


def test_fetch_latest_water_level_data():

    time.sleep(0.1)

    # don't use cache first
    test_data = fetch_latest_water_level_data()
    assert test_data is not None
    assert os.path.isfile(os.path.join('cache', 'level_data.json'))

    # use cache
    test_data = fetch_latest_water_level_data(use_cache=True)
    assert test_data is not None

    # try again, with the cache already existing
    test_data = fetch_latest_water_level_data(use_cache=True)
    assert test_data is not None


def test_build_station_list():

    time.sleep(0.1)

    # Build list, expect station Cam to be found
    stations = build_station_list()
    assert len(stations) > 0
    station_cam = list(filter(lambda s: s.name == 'Cam', stations))[0]
    assert station_cam

    # Fetch data over past 2 days
    dt = 2
    dates2, levels2 = fetch_measure_levels(
        station_cam.measure_id, dt=datetime.timedelta(days=dt))
    assert len(dates2) == len(levels2)

    # Fetch data over past 10 days
    dt = 10
    dates10, levels10 = fetch_measure_levels(
        station_cam.measure_id, dt=datetime.timedelta(days=dt))
    assert len(dates10) == len(levels10)
    assert len(dates10) > len(levels2)
