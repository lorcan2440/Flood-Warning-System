'''
This module provides a model for a monitoring station, and tools
for manipulating/modifying station data
'''


class MonitoringStation:

    '''
    This class represents a river level monitoring station
    '''

    # List of attributes to encapsulate
    _attrs = ['station_id', 'measure_id', 'name', 'coord', 'typical_range', 'river', 'town']

    def __init__(self, station_id, measure_id, label, coord, typical_range,
                 river, town):

        self.__station_id = station_id
        self.__measure_id = measure_id

        # Handle case of erroneous data where data system returns
        # '[label, label]' rather than 'label'
        self.__name = label
        if isinstance(label, list):
            self.__name = label[0]

        self.__coord = coord
        self.__typical_range = typical_range
        self.__river = river
        self.__town = town

        self.latest_level = None

    def __repr__(self):
        d = "Station name:     {}\n".format(self.__name)
        d += "   id:            {}\n".format(self.__station_id)
        d += "   measure id:    {}\n".format(self.__measure_id)
        d += "   coordinate:    {}\n".format(self.__coord)
        d += "   town:          {}\n".format(self.__town)
        d += "   river:         {}\n".format(self.__river)
        d += "   typical range: {}".format(self.__typical_range)
        return d

    # Class methods - make setters private to this class

    @property
    def station_id(self):
        return self.__station_id

    @station_id.setter
    def station_id(self, value):
        self.__station_id = value

    @property
    def measure_id(self):
        return self.__measure_id

    @measure_id.setter
    def measure_id(self, value):
        self.__measure_id = value

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        self.__name = value

    @property
    def coord(self):
        return self.__coord

    @coord.setter
    def coord(self, value):
        self.__coord = value

    @property
    def typical_range(self):
        return self.__typical_range

    @typical_range.setter
    def typical_range(self, value):
        self.__typical_range = value

    @property
    def river(self):
        return self.__river

    @river.setter
    def river(self, value):
        self.__river = value

    @property
    def town(self):
        return self.__town

    @town.setter
    def town(self, value):
        self.__town = value

    # Regular methods

    def typical_range_consistent(self):

        '''
        Returns a bool, whether or not the instance's typical_range
        attribute is well-defined and consistent (correctly ordered),
        returning True if it is and False otherwise.
        '''

        try:
            low_val = self.__typical_range[0]
            high_val = self.__typical_range[1]
            if low_val is None or high_val is None or low_val > high_val:
                # One of the entries was a NoneType,
                # or it was in the wrong order
                # or was negative
                return False
            # Nothing triggered --> consistent
            return True

        except (TypeError, IndexError):
            # Data was itself a NoneType, or otherwise could not be
            # indexed --> inconsistent
            return False

    def relative_water_level(self):

        '''
        Returns the current water level as a fraction of
        the typical range, such that low = 0 and high = 1.
        '''

        try:
            if self.typical_range_consistent():
                level_diff = self.__typical_range[1] - self.__typical_range[0]
                return (self.latest_level - self.__typical_range[0]) / level_diff
            else:
                return None
        except Exception:
            return None


def inconsistent_typical_range_stations(stations):

    '''
    Returns a list of stations that have inconsistent data, based
    on the  MonitoringStation.typical_range_consistent() method.
    '''

    # Standard data type input checks
    assert all([isinstance(i, MonitoringStation) for i in stations])

    return [s for s in stations if not s.typical_range_consistent()]
