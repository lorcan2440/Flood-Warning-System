'''
This module provides interface for extracting station data from
JSON objects fetched from the Internet and
'''

# pylint: disable=relative-beyond-top-level

from .datafetcher import fetch_stationdata, fetch_latest_water_level_data, \
    fetch_gauge_data, fetch_latest_rainfall_data
from .station import MonitoringStation, RainfallGauge


def build_station_list(use_cache: bool = True) -> list[MonitoringStation]:
    '''
    Build and return a list of all river level monitoring stations
    based on data fetched from the Environment agency. Each station is
    represented as a MonitoringStation object.

    The available data for some station is incomplete or not
    available.

    #### Arguments

    `use_cache` (bool, default = True): whether to try fetching station data from a local cache

    #### Returns

    list[MonitoringStation]: station objects built from obtained data
    '''

    data, coastal_data = fetch_stationdata(use_cache=use_cache)

    coastal_ids = {s['@id'] for s in coastal_data['items']}

    stations = []
    for e in data["items"]:

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
        is_tidal = e.get('@id', None) in coastal_ids

        stage_scale = e.get('stageScale')
        if stage_scale is not None:
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

        extra = {'station_id': station_id, 'river': river, 'town': town,
            'url_id': url_id, 'is_tidal': is_tidal, 'record_range': record_range}

        s = MonitoringStation(measure_id, label, coord, typical_range, **extra)
        stations.append(s)

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
            s.latest_level = None


def update_rainfall_levels(gauges: list[RainfallGauge]):
    '''
    Attach rainfall data contained in `measure_data` to gauges. Fetches over internet.

    #### Arguments

    `gauges` (list[RainfallGauges]): list of input stations
    '''

    # Fetch level data
    measure_data = fetch_latest_rainfall_data()
    print(measure_data)

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
            g.latest_level = None
