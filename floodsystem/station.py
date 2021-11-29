'''
This module provides a model for a monitoring station, and tools
for manipulating/modifying station data
'''


class MonitoringStation:

    '''
    This class represents a water-level monitoring station. There are over 2000 such stations across
    England, which record the water level at fixed locations on various rivers and coastal sites.

    Information on the data collected is available at
    https://environment.data.gov.uk/flood-monitoring/doc/reference#stations.

    ### Inputs

    #### Required arguments

    `measure_id` (str): a unique URL string giving access to the station's latest measurement.

    `label` (str): the name of the station, usually named after the surrounding village or district.
    Not guaranteed to be unique.

    `coord` (tuple): a coordinate pair giving the (latitude, longitude) position in degrees of the
    station. Available to 6 decimal places, or a resolution of < 10 cm in England.

    `typical_range` (tuple): a pair of (smaller value, larger value) giving the interval within which
    the middle 90% of flood level data (in metres) since recording lies, or ≈1.64 standard deviations
    below and above the mean. Available to 3 decimal places, or a resolution of 1 mm. Can be reliably
    assumed to be constant over time, although not strictly guaranteed.

    #### Optional arguments

    `latest_level` (str, default = None): the most recent water level recorded at this station.
    Recorded in metres and available to 3 decimal places, or a resolution of 1 mm.

    `latest_recorded_datetime` (datetime.datetime, default = None): the date and time when the most
    recent water level was recorded at this station. Usually rounds to the nearest 15 minutes.

    `town` (str, default = None): the name of the nearest town (or named place) to the station.

    `river` (str, default = None): the name of river associated with this monitoring station.

    `is_tidal` (bool, default = False): whether or not this station measures coastal water levels. If true,
    the water level tends to fluctuate periodically by day and night due to the natural effect of tides.

    `station_id` (str, default = None): a unique URL string giving access to its data.

    `url_id` (str, default = None): the RLOI (River Levels On the Internet) ID, used to access the webpage
    associated with the station.

    `record_range` (tuple, default = None): a pair of (min, max) giving the lowest ever and highest ever
    water levels (in metres) since recording for the station began. Recorded to 3 decimal places,
    or a resolution of 1 mm.

    ### Returns

    A `MonitoringStation` instance, which can be passed (either individually or a list of such objects)
    into a variety of API functions available in the separate modules.
    '''

    def __init__(self, measure_id: str, label: str, coord: tuple[float], typical_range: tuple[float],
            **kwargs):

        # required args
        self.measure_id = measure_id
        self.name = label if not isinstance(label, list) else label[0]
        self.coord = coord
        self.typical_range = typical_range

        # default values (if not set in kwargs)
        self.town = None
        self.river = None
        self.is_tidal = False
        self.latest_level = None
        self.latest_recorded_datetime = None
        self.station_id = None
        self.url = ''
        self.url_id = None
        self.record_range = None

        for attr in kwargs:
            setattr(self, attr, kwargs[attr])

        if self.url_id is not None:
            self.url = "https://check-for-flooding.service.gov.uk/station/" + self.url_id
            delattr(self, 'url_id')

    def __repr__(self):

        attrs = set(self.__dict__.keys()) - {'name', 'measure_id', 'coord', 'typical_range', 'latest_level'}
        additional_info = dict([(k, getattr(self, k, None)) for k in sorted(attrs)])

        d = f" Station name: \t \t {self.name} \n"
        d += f" \t measure id: \t \t {self.measure_id} \n"
        d += f" \t coordinate: \t \t {self.coord} \n"
        d += f" \t typical range: \t {self.typical_range} \n"
        d += f" \t latest level: \t \t {self.latest_level} \n"
        d += f" \t additional info: \t {additional_info} \n"
        return d

    # Bound methods

    def typical_range_consistent(self) -> bool:

        '''
        Returns a bool, whether or not the instance's typical_range
        attribute is well-defined and consistent (correctly ordered),
        returning True if it is and False otherwise.
        '''

        try:
            low_val = self.typical_range[0]
            high_val = self.typical_range[1]
            if low_val is None or high_val is None or low_val > high_val \
                    or not isinstance(low_val, (float, int)) or not isinstance(high_val, (float, int)) \
                    or low_val == high_val:
                # One of the entries was a NoneType, or it was in the wrong order, non-number or equal
                return False
            # Nothing triggered --> consistent
            return True

        except (TypeError, IndexError):
            # Data was itself a NoneType, or otherwise could not be indexed --> inconsistent
            return False

    def relative_water_level(self) -> float:

        '''
        Returns the current water level as a fraction of
        the typical range, such that low = 0 and high = 1.
        '''

        if self.typical_range_consistent() and isinstance(self.latest_level, (float, int)):
            level_diff = self.typical_range[1] - self.typical_range[0]
            return (self.latest_level - self.typical_range[0]) / level_diff
        else:
            return None


class RainfallGauge:

    '''
    This class represents a rainfall gauge. There are over 1000 such Tipping Bucket Raingauges
    (TPRs) across England, which record the amount of precipitation in mm.

    Information on the data collected is available at
    https://environment.data.gov.uk/flood-monitoring/doc/rainfall.

    ### Inputs

    #### Required arguments

    `measure_id` (str): a unique URL string giving access to the gauge's latest measurement.

    `coord` (tuple): a coordinate pair giving the (latitude, longitude) position in degrees of the
    station. Accurate only to the nearest 100 m despite being available to 6 decimal places.

    #### Optional arguments

    `latest_level` (str, default = None): the most recent rainfall reading recorded at this gauge.
    Recorded in millimeters and available to 1 decimal places, or a resolution of 0.1 mm.

    `latest_recorded_datetime` (datetime.datetime, default = None): the date and time when the most
    recent rainfall level was recorded at this station. Typically updates once or twice a day, rounded to
    the nearest 15 minutes.

    `period` (float, default = None): the time between successive readings, in seconds.

    `gauge_number` (str, default = None): a unique identifier (numeric string) for the gauge, used to access
    URLs relating to its readings

    `gauge_id` (str, default = None): a URL giving access to gauge data

    ### Returns

    A `RainfallGauge` instance.
    '''

    def __init__(self, measure_id: str, coord: tuple[float], **kwargs):

        # required args
        self.measure_id = measure_id
        self.coord = coord

        # default values (if not set in kwargs)
        self.latest_level = None
        self.latest_recorded_datetime = None
        self.period = None
        self.gauge_number = ''
        self.gauge_id = None

        for attr in kwargs:
            setattr(self, attr, kwargs[attr])

    def __repr__(self):

        attrs = set(self.__dict__.keys()) - {'gauge_number', 'measure_id', 'coord', 'latest_level'}
        additional_info = dict([(k, getattr(self, k, None)) for k in sorted(attrs)])

        d = f" Gauge number: \t \t {self.gauge_number} \n"
        d += f" \t measure id: \t \t {self.measure_id} \n"
        d += f" \t coordinate: \t \t {self.coord} \n"
        d += f" \t latest level: \t \t {self.latest_level} \n"
        d += f" \t additional info: \t {additional_info} \n"
        return d


def inconsistent_typical_range_stations(stations: list[MonitoringStation]) -> list[MonitoringStation]:

    '''
    Returns the stations that have inconsistent data, based
    on the  MonitoringStation.typical_range_consistent() method.
    '''

    # Standard data type input checks
    assert all([isinstance(i, MonitoringStation) for i in stations])

    return list(filter(lambda s: not s.typical_range_consistent(), stations))
