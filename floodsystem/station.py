'''
This module provides a model for a monitoring station, and tools
for manipulating/modifying station data
'''


def apply_property(cls):

    def make_getter(name):
        def getter(self):
            return getattr(self, name)
        return getter

    def make_setter(name):
        def setter(self, val):
            setattr(self, name, val)
        return setter

    for f in cls._attrs:
        getter = make_getter('__' + f)
        setter = make_setter('__' + f)
        setattr(cls, f, property(getter, setter))
    return cls


@apply_property
class MonitoringStation:

    '''
    This class represents a river level monitoring station
    '''

    # list of attributes to encapsulate
    _attrs = ['station_id', 'measure_id', 'name', 'coord', 'typical_range', 'river', 'town']

    def __init__(self, station_id, measure_id, label, coord, typical_range,
                 river, town):

        self.station_id = station_id
        self.measure_id = measure_id

        # Handle case of erroneous data where data system returns
        # '[label, label]' rather than 'label'
        self.name = label
        if isinstance(label, list):
            self.name = label[0]

        self.coord = coord
        self.typical_range = typical_range
        self.river = river
        self.town = town

        self.latest_level = None

    def __repr__(self):
        d = "Station name:     {}\n".format(self.name)
        d += "   id:            {}\n".format(self.station_id)
        d += "   measure id:    {}\n".format(self.measure_id)
        d += "   coordinate:    {}\n".format(self.coord)
        d += "   town:          {}\n".format(self.town)
        d += "   river:         {}\n".format(self.river)
        d += "   typical range: {}".format(self.typical_range)
        return d

    def typical_range_consistent(self):

        '''
        Returns a bool, whether or not the instance's typical_range
        attribute is well-defined and consistent (correctly ordered),
        returning True if it is and False otherwise.
        '''

        try:
            low_val = self.typical_range[0]
            high_val = self.typical_range[1]
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
                level_diff = self.typical_range[1] - self.typical_range[0]
                return (self.latest_level - self.typical_range[0]) / level_diff
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
