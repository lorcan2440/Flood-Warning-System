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
    '''
    Retrieve JSON data from a given API url.

    #### Arguments

    `url` (str): API url from which to fetch data

    #### Returns

    dict: JSON response
    '''

    r = requests.get(url)
    data = r.json()
    return data


def dump(data: dict, filename: str) -> None:
    '''
    Save JSON response to a file, nicely formatted.

    #### Arguments

    `data` (dict): JSON dict
    `filename` (str): save file location
    '''

    f = open(filename, 'w')
    data = json.dump(data, f, indent=4)
    f.close()


def load(filename: str) -> dict:
    '''
    Loads JSON object from file.

    #### Arguments

    `filename` (str): JSON file to load from

    #### Returns

    dict: JSON dict
    '''

    f = open(filename, 'r')
    data = json.load(f)
    f.close()
    return data


def fetch_stationdata(use_cache: bool = True) -> tuple[dict, dict]:
    '''
    Fetch data from Environment Agency for all active river level
    monitoring stations at once via a REST API and return retrieved data as a
    JSON object. Include tidal (coastal) stations separately.

    Fetched data is dumped to a cache file so on subsequent call it can
    optionally be retrieved from the cache file. This is faster than
    retrieval over the internet and avoids excessive calls to the
    Environment Agency service.

    #### Arguments

    `use_cache` (bool, default = True): whether to try fetching station data from a local cache

    #### Returns

    tuple[dict, dict]: full JSON-formatted datasets for all river-level and tidal stations, respectively
    '''

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
    '''
    Fetch latest levels from all measures.

    #### Arguments

    `use_cache` (bool, default = False): whether to use the most recently stored data
    instead of fetching new data

    #### Returns

    dict: JSON-formatted datasets of latest data at each station
    '''

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
    '''
    Fetch measure levels from latest reading and going back a period dt.
    If there are no measurements available within the specified period, returns ([None], [None]).

    #### Arguments

    `station` (Union[MonitoringStation, str]): either an input station instance or its measure_id string
    `dt` (datetime.timedelta): time period for which to look back in history for data

    #### Additional Kwargs and Flags

    `warnings_kwargs`: passed to `floodsystem.analysis.identify_potentially_bad_data()`

    #### Returns

    tuple[list[datetime.datetime], list[float]]: list of dates and their recorded levels, respectively

    #### Raises

    `TypeError`: if the input station was not a MonitoringStation or a str
    `RuntimeWarning`: if potentially bad data is detected from the station
    `RuntimeWarning`: if the station has not recorded any data within the given period dt
    '''

    if not isinstance(station, (MonitoringStation, str)):
        raise TypeError('The first argument must be either a `MonitoringStation` or a '
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
    if data['items'] != []:
        stationdata = fetch(data['items'][0]['@id'])
        station_name = stationdata['items']['measure']['label'].split(' LVL ')[0].split(' - ')[0]
    else:
        warnings.warn(f'The API call to {url} returned an empty list of items (level data).'
            'The station may have been down during this time period; try a larger dt. ', RuntimeWarning)
        return [None], [None]
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
