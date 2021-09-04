'''
This module provides a model for a monitoring station, and tools
for manipulating/modifying station data
'''


class MonitoringStation:

    '''
    This class represents a river level monitoring station
    '''

    def __init__(self, station_id: str, measure_id: str, label: str, coord: tuple[float],
                 typical_range: tuple[float], river: str, town: str, url_id: str = ''):

        self.station_id = station_id
        self.measure_id = measure_id

        # Handle case of erroneous data where data system returns
        # '[label, label]' rather than 'label'
        self.name = label if not isinstance(label, list) else label[0]

        self.coord = coord
        self.typical_range = typical_range
        self.river = river
        self.town = town
        self.url = "https://check-for-flooding.service.gov.uk/station/" + url_id

        self.latest_level = None

    def __repr__(self):
        d = f" Station name: \t \t {self.name} \n"
        d += f" \t id: \t \t \t \t {self.station_id} \n"
        d += f" \t measure id: \t \t {self.measure_id} \n"
        d += f" \t coordinate: \t \t {self.coord} \n"
        d += f" \t town: \t \t \t \t {self.town} \n"
        d += f" \t river: \t \t \t {self.river} \n"
        d += f" \t typical range: \t {self.typical_range} \n"
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
