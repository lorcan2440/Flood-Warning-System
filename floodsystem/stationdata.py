'''
This module provides interface for extracting station data from
JSON objects fetched from the Internet and
'''

# pylint: disable=relative-beyond-top-level

from .datafetcher import fetch_stationdata, fetch_latest_water_level_data
from .station import MonitoringStation


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

    data, coastal_data = fetch_stationdata(use_cache)

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
            m_id_to_value[measure_id] = latest_reading['value']

    # Attach latest reading to station objects
    for s in stations:
        if s.measure_id in m_id_to_value and isinstance(m_id_to_value[s.measure_id], (int, float)):
            s.latest_level = m_id_to_value[s.measure_id]
        else:
            s.latest_level = None
