'''
This module provides interface for extracting station data from
JSON objects fetched from the Internet and
'''

# pylint: disable=relative-beyond-top-level

from . import datafetcher
from .station import MonitoringStation


def build_station_list(use_cache=True) -> list[MonitoringStation]:

    """
    Build and return a list of all river level monitoring stations
    based on data fetched from the Environment agency. Each station is
    represented as a MonitoringStation object.

    The available data for some station is incomplete or not
    available.
    """

    # Fetch station data
    data, coastal_data = datafetcher.fetch_stationdata(use_cache)

    # set of all ids of coastal stations
    coastal_ids = {s['@id'] for s in coastal_data['items']}

    # Build list of MonitoringStation objects
    stations = []
    for e in data["items"]:
        # Extract town and river strings (not always available)
        town = e.get('town', None)
        river = e.get('riverName', None)

        # Attempt to extract typical range (low, high)
        try:
            typical_range = (float(e['stageScale']['typicalRangeLow']),
                             float(e['stageScale']['typicalRangeHigh']))
        except Exception:
            typical_range = None

        try:
            # Create MonitoringStation object if all required data is available, and add to list
            if e['@id'] in coastal_ids:
                s = MonitoringStation(
                    station_id=e['@id'], measure_id=e['measures'][-1]['@id'], label=e['label'],
                    coord=(float(e['lat']), float(e['long'])), typical_range=typical_range,
                    river=river, town=town, url_id=e.get('RLOIid', ''), is_tidal=True)
            else:
                s = MonitoringStation(
                    station_id=e['@id'], measure_id=e['measures'][-1]['@id'], label=e['label'],
                    coord=(float(e['lat']), float(e['long'])), typical_range=typical_range,
                    river=river, town=town, url_id=e.get('RLOIid', ''), is_tidal=False)
            stations.append(s)
        except Exception:
            # Some essential inputs were not available, so skip over
            pass

    return stations


def update_water_levels(stations: list[MonitoringStation]) -> None:

    """
    Attach level data contained in measure_data to stations.
    """

    # Fetch level data
    measure_data = datafetcher.fetch_latest_water_level_data()

    # Build map from measure id to latest reading (value)
    measure_id_to_value = dict()
    for measure in measure_data['items']:
        if 'latestReading' in measure:
            latest_reading = measure['latestReading']
            measure_id = latest_reading['measure']
            measure_id_to_value[measure_id] = latest_reading['value']

    # Attach latest reading to station objects
    for station in stations:
        station.latest_level = measure_id_to_value[station.measure_id] if \
            station.measure_id in measure_id_to_value and \
            isinstance(measure_id_to_value[station.measure_id], float) else None
