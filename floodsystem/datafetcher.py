'''
This module provides functionality for retrieving real-time and
latest time history level data
'''

# pylint: disable=assignment-from-no-return

import datetime
import json
import os
import warnings
import requests
import dateutil.parser

from .analysis import has_rapid_fluctuations


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


def fetch_stationdata(use_cache: bool = True) -> dict:

    """
    Fetch data from Environment agency for all active river level
    monitoring stations via a REST API and return retrieved data as a
    JSON object.

    Fetched data is dumped to a cache file so on subsequent call it can
    optionally be retrieved from the cache file. This is faster than
    retrieval over the Internet and avoids excessive calls to the
    Environment Agency service.
    """

    # URL for retrieving data for active stations with river level monitoring, see
    # http://environment.data.gov.uk/flood-monitoring/doc/reference)
    url = "http://environment.data.gov.uk/flood-monitoring/id/stations?status=Active&parameter=level&qualifier=Stage&_view=full"  # noqa
    sub_dir = 'cache'

    try:
        os.makedirs(sub_dir)
    except FileExistsError:
        pass
    cache_file = os.path.join(sub_dir, 'stationdata.json')

    # Attempt to load station data from file, otherwise fetch over Internet
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

    return data


def fetch_latest_water_level_data(use_cache: bool = False) -> dict:

    """
    Fetch latest levels from all 'measures'. Returns JSON object
    """

    # URL for retrieving data
    url = "http://environment.data.gov.uk/flood-monitoring/id/measures?parameter=level&qualifier=Stage&qualifier=level"  # noqa
    sub_dir = 'cache'

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


def fetch_measure_levels(measure_id: str, dt: datetime.timedelta,
        **warnings_kwargs: dict) -> tuple[list[datetime.datetime], list[float]]:

    """
    Fetch measure levels from latest reading and going back a period
    `dt`. Return list of dates and a list of values.
    """

    # Current time (UTC)
    now = datetime.datetime.utcnow()

    # Start time for data
    start = now - dt

    # Construct URL for fetching data
    url_base = measure_id
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

    flags = identify_potentially_bad_data(station_name, levels, **warnings_kwargs)
    for flag in flags:
        warnings.warn('\n' + flag + '\n', RuntimeWarning)

    return dates, levels


def identify_potentially_bad_data(station_name: str, levels: list[float], **kwargs: dict) -> set:

    NEGATIVE_LEVEL_TO_ZERO      = kwargs.get('negative_level_to_zero',      True)   # noqa
    REPLACE_TUPLE_WITH_INDEX    = kwargs.get('replace_tuple_with_index',    1)      # noqa
    TOO_HIGH_CUTOFF             = kwargs.get('too_high_cutoff',             2500)   # noqa
    TOO_HIGH_TO_PREVIOUS_LEVEL  = kwargs.get('too_high_to_previous_level',  True)   # noqa
    TOO_FAST_INCREASE_CUTOFF    = kwargs.get('too_fast_increase_cutoff',    2)      # noqa
    TOO_FAST_DECREASE_CUTOFF    = kwargs.get('too_fast_decrease_cutoff',    0.3)    # noqa

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
        if levels[i] < 0:

            warn_str = f"Data for {station_name} station may be unreliable. "
            warn_str += "Some water levels were found to be negative. \nThese have been set to 0 m."

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
    if has_rapid_fluctuations(levels):

        warn_str = f"Data for {station_name} station may be unreliable. "
        warn_str += "There are many sudden spikes between consecutive measurements. "
        warn_str += "These values have not been altered."

        flags.add(warn_str)

    return flags
