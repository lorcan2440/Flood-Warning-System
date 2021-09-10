'''
This module provides functionality for retrieving real-time and
latest time history level data

Reference:
https://environment.data.gov.uk/flood-monitoring/doc/reference
'''

# pylint: disable=assignment-from-no-return

import datetime
import json
import os
import warnings
import requests
import dateutil.parser
from typing import Union

from .analysis import identify_potentially_bad_data
from .station import MonitoringStation


def fetch(url: str) -> dict:

    """
    Fetch data from url and return fetched JSON object
    """

    r = requests.get(url)
    data = r.json()
    return data


def dump(data: dict, filename: str) -> None:

    """
    Save JSON object to file
    """

    f = open(filename, 'w')
    data = json.dump(data, f)
    f.close()


def load(filename: str) -> dict:

    """
    Load JSON object from file
    """

    f = open(filename, 'r')
    data = json.load(f)
    f.close()
    return data


def fetch_stationdata(use_cache: bool = True) -> tuple[dict, dict]:

    """
    Fetch data from Environment Agency for all active river level
    monitoring stations at once via a REST API and return retrieved data as a
    JSON object. Include tidal (coastal) stations separately.

    Fetched data is dumped to a cache file so on subsequent call it can
    optionally be retrieved from the cache file. This is faster than
    retrieval over the internet and avoids excessive calls to the
    Environment Agency service.
    """

    # URL for retrieving data for active stations with river level monitoring
    root = "http://environment.data.gov.uk/flood-monitoring/id/stations"

    rest_api_str = "?status=Active&parameter=level&qualifier=Stage&_view=full"
    coastal_only = "&type=Coastal"

    url = root + rest_api_str
    sub_dir = 'cache/data'

    try:
        os.makedirs(sub_dir)
    except FileExistsError:
        pass

    cache_file = os.path.join(sub_dir, 'station_data.json')

    # Attempt to load all station data from file, otherwise fetch over internet
    if use_cache:
        try:
            # Attempt to load from file
            data = load(cache_file)
        except FileNotFoundError:
            # If load from file fails, fetch and dump to file
            data = fetch(url)
            dump(data, cache_file)
    else:
        # Fetch and dump to file
        data = fetch(url)
        dump(data, cache_file)

    url += coastal_only
    coastal_cache_file = os.path.join(sub_dir, 'coastal_station_data.json')

    # Attempt to load coastal station data from file, otherwise fetch over internet
    if use_cache:
        try:
            # Attempt to load from file
            coastal_data = load(coastal_cache_file)
        except FileNotFoundError:
            # If load from file fails, fetch and dump to file
            coastal_data = fetch(url)
            dump(coastal_data, coastal_cache_file)
    else:
        # Fetch and dump to file
        coastal_data = fetch(url)
        dump(coastal_data, coastal_cache_file)

    return data, coastal_data


def fetch_latest_water_level_data(use_cache: bool = False) -> dict:

    """
    Fetch latest levels from all 'measures'. Returns JSON object
    """

    # URL for retrieving data
    root = "http://environment.data.gov.uk/flood-monitoring/id/measures"
    rest_api_str = "?parameter=level&qualifier=Stage&qualifier=level"
    url = root + rest_api_str
    sub_dir = 'cache/data'

    try:
        os.makedirs(sub_dir)
    except FileExistsError:
        pass
    cache_file = os.path.join(sub_dir, 'level_data.json')

    # Attempt to load level data from file, otherwise fetch over internet (slower)
    if use_cache:
        try:
            # Attempt to load from file
            data = load(cache_file)
        except FileNotFoundError:
            data = fetch(url)
            dump(data, cache_file)
    else:
        data = fetch(url)
        dump(data, cache_file)

    return data


def fetch_measure_levels(station: Union[MonitoringStation, str], dt: datetime.timedelta,
        **warnings_kwargs: dict) -> tuple[list[datetime.datetime], list[float]]:

    """
    Fetch measure levels from latest reading and going back a period
    `dt`. Return list of dates and a list of values.

    `station` can be either a `MonitoringStation` instance, or a `measure_id` string.
    """

    if not isinstance(station, (MonitoringStation, str)):
        raise ValueError('The first argument must be either a `MonitoringStation` or a '
        f'measure_id string.\nGot value {station} of type {type(station)}')

    # Current time (UTC)
    now = datetime.datetime.utcnow()

    # Start time for data
    start = now - dt

    # Construct URL for fetching data
    url_base = station.measure_id if isinstance(station, MonitoringStation) else station
    url_options = "/readings/?_sorted&since=" + start.isoformat() + 'Z'
    url = url_base + url_options

    # Fetch data
    data = fetch(url)
    stationdata = fetch(data['items'][0]['@id'])
    station_name = stationdata['items']['measure']['label'].split(' LVL ')[0].split(' - ')[0]
    flags = {}

    # Extract dates and levels
    dates, levels = [], []
    for measure in reversed(data['items']):
        # Convert date-time string to a datetime object
        d = dateutil.parser.parse(measure['dateTime'])

        # Append data
        dates.append(d)
        levels.append(measure['value'])

    flags = identify_potentially_bad_data(station_name, levels,
        station_obj=station if isinstance(station, MonitoringStation) else None, **warnings_kwargs)
    for flag in flags:
        warnings.warn('\n' + flag + '\n', RuntimeWarning)

    return dates, levels
