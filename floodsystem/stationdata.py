'''
This module provides interface for extracting station data from
JSON objects fetched from the Internet.
'''

# built-in libraries
from itertools import groupby
import warnings

# local imports
try:
    from .datafetcher import \
        fetch_stationdata, fetch_latest_water_level_data, fetch_gauge_data, \
        fetch_latest_rainfall_data, fetch_upstream_downstream_stations
    from .station import MonitoringStation, RainfallGauge
except ImportError:
    from datafetcher import \
        fetch_stationdata, fetch_latest_water_level_data, fetch_gauge_data, \
        fetch_latest_rainfall_data, fetch_upstream_downstream_stations
    from station import MonitoringStation, RainfallGauge


def build_station_list(use_cache: bool = True, return_numbers: bool = False) -> list[MonitoringStation]:
    '''
    Build and return a list of all river level monitoring stations
    based on data fetched from the Environment agency. Each station is
    represented as a MonitoringStation object.

    The available data for some stations is incomplete or not available.

    #### Arguments

    `use_cache` (bool, default = True): whether to try fetching station data from a local cache
    `return_numbers` (bool, default = False): whether to additionally return a second value,
        the numbers of river-level, tidal and groundwater stations found respectively

    #### Returns

    list[MonitoringStation]: station objects built from obtained data
    dict[str, int] (if `return_numbers`): a mapping of the number of types of station found, in the form
        {'River Level': #, 'Tidal': #, 'Groundwater': #}
    '''

    river_data, coastal_data, groundwater_data = fetch_stationdata(use_cache=use_cache)

    coastal_ids = {s['@id'] for s in coastal_data['items']}
    groundwater_ids = {s['@id'] for s in groundwater_data['items']}

    stations = []
    for e in river_data["items"] + coastal_data["items"] + groundwater_data["items"]:

        station_id = e.get('@id', None)

        measures = e.get('measures', None)
        if measures is not None or measures in {[], [{}], [None], {None}}:
            measure_id = measures[-1]['@id']
        else:
            continue  # essential field: no measure means nothing to get data from, so skip

        label = e['label']
        lat = e.get('lat', None)
        long = e.get('long', None)
        if lat is None or long is None:
            coord = None
        else:
            coord = (float(lat), float(long))

        town = e.get('town', None)
        river = e.get('riverName', None)
        url_id = e.get('RLOIid', '')
        url = 'https://check-for-flooding.service.gov.uk/station/' + url_id
        is_tidal = station_id in coastal_ids
        is_groundwater = station_id in groundwater_ids

        stage_scale = e.get('stageScale')
        if stage_scale is not None and not isinstance(stage_scale, str):
            typical_range_low = stage_scale.get('typicalRangeLow', None)
            typical_range_high = stage_scale.get('typicalRangeHigh', None)

            if typical_range_low is None or typical_range_high is None:
                typical_range = None
            else:
                typical_range = (float(typical_range_low), float(typical_range_high))

            min_on_record = stage_scale.get('minOnRecord', None)
            max_on_record = stage_scale.get('maxOnRecord', None)
            if min_on_record is not None:
                min_on_record = min_on_record.get('value', None)
            if max_on_record is not None:
                max_on_record = max_on_record.get('value', None)
            if min_on_record is None or max_on_record is None:
                record_range = None
            else:
                record_range = (float(min_on_record), float(max_on_record))
        else:
            typical_range = record_range = None

        if not (is_tidal or is_groundwater):
            station_type = 'River Level'
        elif is_tidal and not is_groundwater:
            station_type = 'Tidal'
        elif is_groundwater and not is_tidal:
            station_type = 'Groundwater'
        else:
            station_type = None

        extra = {'station_id': station_id, 'river': river, 'town': town,
            'url': url, 'url_id': url_id, 'is_tidal': is_tidal, 'is_groundwater': is_groundwater,
            'record_range': record_range, 'station_type': station_type,
            'upstream_url_id': None, 'downstream_url_id': None}

        s = MonitoringStation(measure_id, label, coord, typical_range, **extra)
        stations.append(s)

    # add upstream/downstream attrs separately
    urls = [s.url for s in stations]
    stream_mappings = fetch_upstream_downstream_stations(urls, use_cache=use_cache)
    station_mappings = {s.url_id: s for s in stations}
    for url_id, s in station_mappings.items():
        if url_id in stream_mappings:
            s.upstream_url_id = stream_mappings[url_id]['upstream']
            s.downstream_url_id = stream_mappings[url_id]['downstream']
        else:
            warnings.warn(f'Station ID {url_id} not found in current upstream/downstream cache - '
                          'to record this information, run this function with `use_cache=False`.')

    if return_numbers:
        nums = {k: len(list(v)) for k, v in groupby(stations, key=lambda s: s.station_type)}
        return stations, nums
    else:
        return stations


def build_rainfall_gauge_list(use_cache: bool = True) -> list[MonitoringStation]:
    '''
    Build and return a list of all rainfall gauges based on data fetched from
    the Environment agency. Each gauge is represented as a RainfallGauge object.

    The available data for some gauges is incomplete or not available.

    #### Arguments

    `use_cache` (bool, default = True): whether to try fetching gauge data from a local cache

    #### Returns

    list[RainfallGauge]: gauge objects built from obtained data
    '''

    data = fetch_gauge_data(use_cache=use_cache)

    gauges = []
    for e in data['items']:
        gauge_id = e.get('@id', None)
        lat = e.get('lat', None)
        long = e.get('long', None)

        if (measures := e['measures']) != []:
            measure_id = measures[0].get('@id', None)
            period = measures[0].get('period', None)
        else:
            measure_id = None
            period = None

        if lat is None or long is None or measure_id is None:
            # essential fields, so skip if not available
            continue
        else:
            coord = (float(lat), float(long))

        gauge_number = e.get('stationReference', None)
        extra = {'period': period, 'gauge_number': gauge_number, 'gauge_id': gauge_id}

        g = RainfallGauge(measure_id, coord, **extra)
        gauges.append(g)

    return gauges


def update_water_levels(stations: list[MonitoringStation]):
    '''
    Attach level data contained in `measure_data` to stations. Fetches over internet.

    #### Arguments

    `stations` (list[MonitoringStation]): list of input stations
    '''

    # Fetch level data
    measure_data = fetch_latest_water_level_data()

    # Build map from measure id to latest reading (value)
    m_id_to_value = dict()
    for measure in measure_data['items']:
        if 'latestReading' in measure:
            latest_reading = measure['latestReading']
            measure_id = latest_reading['measure']
            m_id_to_value[measure_id] = (latest_reading['value'], latest_reading['dateTime'])

    # Attach latest reading to station objects
    for s in stations:
        if s.measure_id in m_id_to_value:
            s.latest_level, s.latest_recorded_datetime = m_id_to_value[s.measure_id]
        else:
            s.latest_level, s.latest_recorded_datetime = None, None


def update_rainfall_levels(gauges: list[RainfallGauge]):
    '''
    Attach rainfall data contained in `measure_data` to gauges. Fetches over internet.

    #### Arguments

    `gauges` (list[RainfallGauges]): list of input stations
    '''

    # Fetch level data
    measure_data = fetch_latest_rainfall_data()

    # Build map from measure id to latest reading (value)
    m_id_to_value = dict()
    for measure in measure_data['items']:
        if 'latestReading' in measure:
            latest_reading = measure['latestReading']
            measure_id = latest_reading['measure']
            m_id_to_value[measure_id] = (latest_reading['value'], latest_reading['dateTime'])

    # Attach latest reading to station objects
    for g in gauges:
        if g.measure_id in m_id_to_value:
            g.latest_level, g.latest_recorded_datetime = m_id_to_value[g.measure_id]
        else:
            g.latest_level, g.latest_recorded_datetime = None, None


def get_station_by_name(stations: list[MonitoringStation], name: str) -> MonitoringStation:
    '''
    Gets the station with a particular name. Assumed unique, so returns one station.

    #### Arguments

    `stations` (list[MonitoringStation]): list of stations to search
    `name` (str): name attribute to match

    #### Returns

    MonitoringStation: the station with the corresponding name

    #### Raises

    `ValueError`: if the name is not found within the given list
    '''
    try:
        station = next(s for s in stations if s.name == name)
        return station
    except (UnboundLocalError, StopIteration):
        raise ValueError(f'A station with name {name} could not be found in the given list.')


def get_station_by_url_id(stations: list[MonitoringStation], url_id: str) -> MonitoringStation:
    '''
    Gets the station with a particular url_id. Assumed unique, so returns one station.

    #### Arguments

    `stations` (list[MonitoringStation]): list of stations to search
    `url_id` (str): url_id attribute to match

    #### Returns

    MonitoringStation: the station with the corresponding url_id

    #### Raises

    `ValueError`: if the url_id is not found within the given list
    '''
    try:
        station = next(s for s in stations if s.url_id == url_id)
        return station
    except (UnboundLocalError, StopIteration):
        raise ValueError(f'A station with url_id = {url_id} could not be found in the given list.')


def get_station_by_attrs(stations: list[MonitoringStation], attr_name_vals: dict[str, str],
        return_one: bool = True) -> MonitoringStation:
    '''
    Gets the station with particular attribute(s).

    #### Example

    ```
    from floodsystem.stationdata import build_station_list, get_station_by_attrs
    stations = build_station_list()
    station_cam = get_station_by_attrs(stations, {'name': 'Cam'})
    print(station_cam)
    ```

    #### Arguments

    `stations` (list[MonitoringStation]): list of stations to search
    `attr_name_vals` (dict): a mapping of attributes to filter on and the values to match.

    #### Keyword Arguments

    `return_one` (bool, default = True): if True, assumes only one
    station will match the given filter and returns it.
    If False, instead returns a list of all matching stations.

    #### Returns

    MonitoringStation: the station with the matching attribute values

    #### Raises

    `ValueError`: if no matches are found within the given list
    '''

    if return_one:
        try:
            station = next(s for s in stations if all(
                [getattr(s, attr, None) == val for attr, val in attr_name_vals.items()]))
            return station
        except (UnboundLocalError, StopIteration):
            raise ValueError(f'A station matching {attr_name_vals} could '
            'not be found in the given list.')
    else:
        matches = list(filter(
            lambda s: all([getattr(s, attr, None) == val for attr, val in attr_name_vals.items()]),
            stations))
        if matches != []:
            return matches
        else:
            raise ValueError(f'A station matching {attr_name_vals} could '
            'not be found in the given list.')
