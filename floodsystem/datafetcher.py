'''
This module provides functionality for retrieving real-time and
latest time history level data

Reference:
https://environment.data.gov.uk/flood-monitoring/doc/reference
'''

# built-in libraries
import datetime
import json
import os
import warnings
import requests
from typing import Union

# third party libraries
import dateutil
from bs4 import BeautifulSoup

# local imports
try:
    from .analysis import identify_potentially_bad_data
    from .station import MonitoringStation, RainfallGauge
except ImportError:
    from analysis import identify_potentially_bad_data
    from station import MonitoringStation, RainfallGauge


CACHE_DIR = 'cache/data'


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

    with open(filename, 'w') as f:
        data = json.dump(data, f, indent=4)


def load(filename: str) -> dict:
    '''
    Loads JSON object from file.

    #### Arguments

    `filename` (str): JSON file to load from

    #### Returns

    dict: JSON dict
    '''

    with open(filename, 'r') as f:
        data = json.load(f)

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

    tuple[dict, dict, dict]: full JSON-formatted datasets for all river-level,
    tidal and groundwater stations, respectively
    '''

    # URL for retrieving data for active stations with river level monitoring
    ROOT_URL = "http://environment.data.gov.uk/flood-monitoring/id/stations"
    API_STR = "?status=Active&parameter=level&_view=full"
    RIVER_ONLY = "&type=SingleLevel"
    COASTAL_ONLY = "&type=Coastal"
    GROUNDWATER_ONLY = "&type=Groundwater"
    url = ROOT_URL + API_STR

    if not os.path.isdir(CACHE_DIR):
        os.makedirs(CACHE_DIR)

    river_cache_file = os.path.join(CACHE_DIR, 'station_data_river.json')
    coastal_cache_file = os.path.join(CACHE_DIR, 'station_data_coastal.json')
    groundwater_cache_file = os.path.join(CACHE_DIR, 'station_data_groundwater.json')

    # Attempt to load all river data from file, otherwise fetch over internet
    if use_cache and all([os.path.isfile(f) for f in
            {river_cache_file, coastal_cache_file, groundwater_cache_file}]):
        try:
            river_data = load(river_cache_file)
            coastal_data = load(coastal_cache_file)
            groundwater_data = load(groundwater_cache_file)
        except Exception:
            return fetch_stationdata(use_cache=False)
    else:
        # Fetch and dump to file
        river_data = fetch(url + RIVER_ONLY)
        dump(river_data, river_cache_file)
        coastal_data = fetch(url + COASTAL_ONLY)
        dump(coastal_data, coastal_cache_file)
        groundwater_data = fetch(url + GROUNDWATER_ONLY)
        dump(groundwater_data, groundwater_cache_file)

    return river_data, coastal_data, groundwater_data


def fetch_upstream_downstream_stations(urls: list[str], use_cache: bool = True,
        save_to_cache: bool = True) -> tuple[str, str]:

    '''
    Fetches the station id which is upstream and downstream of the station with given url.
    Returns None if no station is found upstream/downstream.

    NOTE: *without* cache, takes ~0.3 seconds per url, or ~10 mins to rebuild
    the full station dataset.

    #### Arguments

    `urls` (list[str]): a list of all station urls to find, as given by MonitoringStation.url

    #### Returns

    dict[str, dict]: a mapping of each url_id given to its upstream and downstream url_id
    ```
    {this_url_id: {'upstream': upstream_url_id, 'downstream': downstream_url_id}}
    ```
    '''

    if not os.path.isdir(CACHE_DIR):
        os.makedirs(CACHE_DIR)

    stream_cache = os.path.join(CACHE_DIR, 'station_data_upstream_downstream.json')

    if use_cache and os.path.isfile(stream_cache):
        mappings = load(stream_cache)
        if len(urls) != len(mappings):
            # if there have been stations added since the cache was last made, get them now
            urls_not_found = filter(lambda u: u.split('/')[-1] not in mappings, urls)
            new_mappings = fetch_upstream_downstream_stations(list(urls_not_found),
                use_cache=False, save_to_cache=False)
            mappings.update(new_mappings)
    else:
        # find upstream/downstream by scraping from web pages (slow).
        # NOTE: Accessed by webscraping with `beautifulsoup4` as this information is
        # not currently provided by the API - it has been marked as a potential future
        # improvement in correspondence with enquiries@environment-agency.gov.uk.
        mappings = {}
        for i, url in enumerate(urls):
            print(f'({i} / {len(urls)}) Fetching from {url}')
            webpage_html = requests.get(url).text
            downstream_id, upstream_id = None, None
            soup = BeautifulSoup(webpage_html, features='lxml')
            for link in soup.find_all('a', class_='defra-flood-nav__link'):
                link_class = link['class']
                if len(link_class) > 1:
                    if link_class[-1] == 'defra-flood-nav__link--downstream':
                        downstream_id = link['href'].split('/')[-1]
                    if link_class[-1] == 'defra-flood-nav__link--upstream':
                        upstream_id = link['href'].split('/')[-1]
            mappings[url.split('/')[-1]] = {'upstream': upstream_id, 'downstream': downstream_id}

    # cache data in mappings dict if needed
    if save_to_cache:
        dump(mappings, stream_cache)

    return mappings


def fetch_gauge_data(use_cache: bool = False) -> dict:
    '''
    Fetch data from Environment Agency for all active rainfall gauges
    at once via a REST API and return retrieved data as a JSON object.

    Fetched data is dumped to a cache file so on subsequent call it can
    optionally be retrieved from the cache file. This is faster than
    retrieval over the internet and avoids excessive calls to the
    Environment Agency service.

    #### Arguments

    `use_cache` (bool, default = False): whether to use the most recently stored data
    instead of fetching new data

    #### Returns

    dict: full JSON-formatted datasets for all gauges
    '''

    ROOT_URL = 'https://environment.data.gov.uk/flood-monitoring/id/'
    API_STR = 'stations?parameter=rainfall'
    url = ROOT_URL + API_STR

    if not os.path.isdir(CACHE_DIR):
        os.makedirs(CACHE_DIR)

    cache_file = os.path.join(CACHE_DIR, 'rainfall_gauge_data.json')

    # Attempt to load level data from file, otherwise fetch over internet (slower)
    if use_cache and os.path.isfile(cache_file):
        try:
            # Attempt to load from file
            rainfall_data = load(cache_file)
        except FileNotFoundError:
            return fetch_gauge_data(use_cache=False)
    else:
        rainfall_data = fetch(url)
        dump(rainfall_data, cache_file)

    return rainfall_data


def fetch_latest_water_level_data(use_cache: bool = False) -> dict:
    '''
    Fetch latest water levels from all measures (stations).

    #### Arguments

    `use_cache` (bool, default = False): whether to use the most recently stored data
    instead of fetching new data

    #### Returns

    dict: JSON-formatted datasets of latest data at each station
    '''

    # URL for retrieving data
    ROOT_URL = "http://environment.data.gov.uk/flood-monitoring/id/measures"
    API_STR = "?parameter=level"
    url = ROOT_URL + API_STR

    if not os.path.isdir(CACHE_DIR):
        os.makedirs(CACHE_DIR)

    cache_file = os.path.join(CACHE_DIR, 'station_water_level_data.json')

    # Attempt to load level data from file, otherwise fetch over internet (slower)
    if use_cache and os.path.isfile(cache_file):
        try:
            # Attempt to load from file
            level_data = load(cache_file)
        except FileNotFoundError:
            return fetch_latest_water_level_data(use_cache=False)
    else:
        level_data = fetch(url)
        dump(level_data, cache_file)

    return level_data


def fetch_latest_rainfall_data(use_cache: bool = False) -> dict:
    '''
    Fetch latest rainfall levels from all measures (gauges).

    #### Arguments

    `use_cache` (bool, default = False): whether to use the most recently stored data
    instead of fetching new data

    #### Returns

    dict: JSON-formatted datasets of latest data at each gauge
    '''

    # URL for retrieving data
    ROOT_URL = "https://environment.data.gov.uk/flood-monitoring/id/measures"
    API_STR = "?parameter=rainfall"
    url = ROOT_URL + API_STR

    try:
        os.makedirs(CACHE_DIR)
    except FileExistsError:
        pass
    cache_file = os.path.join(CACHE_DIR, 'rainfall_water_level_data.json')

    # Attempt to load level data from file, otherwise fetch over internet (slower)
    if use_cache:
        try:
            # Attempt to load from file
            level_data = load(cache_file)
        except FileNotFoundError:
            return fetch_latest_rainfall_data(use_cache=False)
    else:
        level_data = fetch(url)
        dump(level_data, cache_file)

    return level_data


def fetch_measure_levels(station: Union[MonitoringStation, str], dt: datetime.timedelta,
        **warnings_kwargs: dict) -> tuple[list[datetime.datetime], list[float]]:
    '''
    Fetch measure levels for one station from latest reading and going back a period dt.
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
        if (value := measure.get('value', None)) is not None:
            dates.append(d)
            levels.append(value)

    flags = identify_potentially_bad_data(station_name, levels,
        station_obj=station if isinstance(station, MonitoringStation) else None,
        data_origin_type='RIVER_STATION', **warnings_kwargs)
    for flag in flags:
        warnings.warn('\n' + flag + '\n', RuntimeWarning)

    return dates, levels


def fetch_rainfall_levels(gauge: Union[RainfallGauge, str], dt: datetime.timedelta,
        **warnings_kwargs: dict) -> tuple[list[datetime.datetime], list[float]]:
    '''
    Fetch rainfall for one gauge from latest reading and going back a period dt.
    If there are no measurements available within the specified period, returns ([None], [None]).

    #### Arguments

    `gauge` (Union[RainfallGauge, str]): either an input station instance or its measure_id string
    `dt` (datetime.timedelta): time period for which to look back in history for data

    #### Additional Kwargs and Flags

    `warnings_kwargs`: passed to `floodsystem.analysis.identify_potentially_bad_data()`

    #### Returns

    tuple[list[datetime.datetime], list[float]]: list of dates and their recorded levels, respectively

    #### Raises

    `TypeError`: if the input gauge was not a RainfallGauge or a str
    `RuntimeWarning`: if potentially bad data is detected from the gauge
    `RuntimeWarning`: if the gauge has not recorded any data within the given period dt
    '''

    if not isinstance(gauge, (RainfallGauge, str)):
        raise TypeError('The first argument must be either a `RainfallGauge` or a '
        f'measure_id string.\nGot value {gauge} of type {type(gauge)}')

    # Current time (UTC)
    now = datetime.datetime.utcnow()

    # Start time for data
    start = now - dt

    # Construct URL for fetching data
    url_base = gauge.measure_id if isinstance(gauge, RainfallGauge) else gauge
    url_options = "/readings?_sorted&since=" + start.isoformat() + 'Z'
    url = url_base + url_options
    gauge_number = url_base.split('/')[-1]

    # Fetch data
    data = fetch(url)
    if data['items'] == []:
        warnings.warn(f'The API call to {url} returned an empty list of items (level data).'
            'The gauge may have been down during this time period; try a larger dt. ', RuntimeWarning)
        return [None], [None]
    flags = {}

    # Extract dates and rainfall readings
    dates, rainfalls = [], []
    for measure in reversed(data['items']):
        # Convert date-time string to a datetime object
        d = dateutil.parser.parse(measure['dateTime'])

        # Append data
        dates.append(d)
        rainfalls.append(measure['value'])

    flags = identify_potentially_bad_data(f'Rainfall Gauge #{gauge_number}', rainfalls,
        station_obj=gauge if isinstance(gauge, RainfallGauge) else None,
        data_origin_type='RAINFALL_GAUGE', **warnings_kwargs)
    for flag in flags:
        warnings.warn('\n' + flag + '\n', RuntimeWarning)

    return dates, rainfalls
