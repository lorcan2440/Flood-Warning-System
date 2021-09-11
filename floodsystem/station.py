'''
This module provides a model for a monitoring station, and tools
for manipulating/modifying station data
'''


class MonitoringStation:

    '''
    This class represents a river level monitoring station
    '''

    def __init__(self, measure_id: str, label: str, coord: tuple[float], typical_range: tuple[float],
            **kwargs):

        self.measure_id = measure_id
        self.name = label if not isinstance(label, list) else label[0]
        self.coord = coord
        self.typical_range = typical_range

        for attr in kwargs:
            setattr(self, attr, kwargs[attr])

        if hasattr(self, 'url_id'):
            self.url = "https://check-for-flooding.service.gov.uk/station/" + self.url_id
            delattr(self, 'url_id')
        else:
            self.url = None

        if not hasattr(self, 'latest_level'):
            self.latest_level = None

    def __repr__(self):

        attrs = set(self.__dict__.keys()) - {'name', 'measure_id', 'coord', 'typical_range', 'latest_level'}
        additional_info = dict([(k, getattr(self, k, None)) for k in sorted(attrs)])

        d = f" Station name: \t \t {self.name} \n"
        d += f" \t measure id: \t \t {self.measure_id} \n"
        d += f" \t coordinate: \t \t {self.coord} \n"
        d += f" \t typical range: \t {self.typical_range} \n"
        d += f" \t latest level: \t \t {getattr(self, 'latest_level', None)} \n"
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


def inconsistent_typical_range_stations(stations: list[MonitoringStation]) -> list[MonitoringStation]:

    '''
    Returns the stations that have inconsistent data, based
    on the  MonitoringStation.typical_range_consistent() method.
    '''

    # Standard data type input checks
    assert all([isinstance(i, MonitoringStation) for i in stations])

    return list(filter(lambda s: not s.typical_range_consistent(), stations))
