'''
This module contains utility functions.

Source code for Haversine functions adapted from
https://pypi.org/project/haversine/; version 2.3.0, accessed Sep 4, 2020
'''

# built-in libraries
import warnings
import os
from math import radians, degrees, sin, cos, tan, asin, sqrt, log, pi
from enum import Enum
import multiprocessing as mp

# third-party libraries
import dill


class Unit(Enum):

    """
    Enumeration of supported units.
    The full list can be checked by iterating over the class; e.g.
    the expression `tuple(Unit)`.
    """

    KILOMETERS = 'km'
    METERS = 'm'
    MILES = 'mi'
    NAUTICAL_MILES = 'nmi'
    FEET = 'ft'
    INCHES = 'in'


# Unit values taken from http://www.unitconversion.org/unit_converter/length.html
_CONVERSIONS = {Unit.KILOMETERS:        1.0,                # noqa
                Unit.METERS:            1000.0,             # noqa
                Unit.MILES:             0.621371192,        # noqa
                Unit.NAUTICAL_MILES:    0.539956803,        # noqa
                Unit.FEET:              3280.839895013,     # noqa
                Unit.INCHES:            39370.078740158}    # noqa

# mean earth radius - https://en.wikipedia.org/wiki/Earth_radius#Mean_radius
_AVG_EARTH_RADIUS_KM = 6371.0088


def patch_multiprocessing_pickler():
    '''
    Replace the multiprocessing pickler with that of dill:
    https://dill.readthedocs.io/en/latest/dill.html

    Allows serialisation of a wider variety of objects, including closures with inner functions.
    Required to allow multiprocessing on the Flask server.
    '''

    dill.Pickler.dumps, dill.Pickler.loads = dill.dumps, dill.loads
    mp.reduction.ForkingPickler = dill.Pickler
    mp.reduction.dump = dill.dump


def sorted_by_key(nested_list: list[tuple], index: int, reverse: bool = False) -> list[tuple]:
    '''
    For a list of lists/tuples, return list sorted by the ith
    component of the list/tuple.
    '''

    return sorted(nested_list, key=lambda x: x[index], reverse=reverse)


def wgs84_to_web_mercator(coord: tuple[float]) -> tuple[float]:
    '''
    Returns a tuple of web mercator (x, y) coordinates compatible with the
    Bokeh plotting module given a tuple of (lat, long) coords.
    https://en.wikipedia.org/wiki/Web_Mercator_projection

    Actual support for Google Maps is latitude between -85.06 and 85.06.
    '''
    if coord is None:
        return (None, None)

    if not bool(-90 < coord[0] < 90 and -180 <= coord[1] <= 180):
        raise ValueError('Latitude must be between -90 and 90, '
        'and Longitude must be between -180 and 180.')

    lat, long = coord[0], coord[1]
    R_MAJOR = 6378137.000  # (major) radius of earth in m
    x = R_MAJOR * radians(long)
    if long != 0:
        y = degrees(log(tan(pi / 4 + 0.5 * radians(lat))) * (x / long))
    else:
        y = log(tan(pi / 4 + 0.5 * radians(lat))) * R_MAJOR
    return (x, y)


def flatten(t: list[list]) -> list:
    '''
    Given a list of lists, returns a single list containing all
    the elements of each list in the original list. Also works
    with tuples (but not sets or dicts)
    '''

    return [item for sublist in t for item in sublist]


def coord_letters(lat: float, long: float) -> tuple[str, str]:
    '''
    Determines whether a coordinate is in the North/South and East/West hemispheres
    and assigns them a corresponding letter.

    The Equator is considered North and the Prime Meridian is considered East.
    '''

    return ('N' if lat >= 0 else 'S', 'E' if long >= 0 else 'W')


def get_avg_earth_radius(unit: Enum) -> float:
    '''
    Returns the average radius of the Earth in the chosen units.
    '''

    unit = Unit(unit)
    return _AVG_EARTH_RADIUS_KM * _CONVERSIONS[unit]


def read_only_properties(*attrs):
    '''
    Decorator for making attributes of a class read-only (values should not be set after initialisation).

    #### Arguments

    `attrs` (list[str]): string names of the attributes of the class to make read-only.
    '''

    def class_setattr_editor(cls):
        "The class decorator"

        def read_only_setattr(self, name, value):

            if name in attrs and name in self.__dict__:
                raise AttributeError(f'The attribute {name} is read-only. ' +    # noqa
                    'It should not be set after initialisation.')

            super(cls, self).__setattr__(name, value)

        setattr(cls, '__setattr__', read_only_setattr)
        return cls

    return class_setattr_editor


def hide_tensorflow_debug_logs():

    '''
    Disables initialisation warnings from tensorflow

    Source:
    https://stackoverflow.com/questions/35911252/disable-tensorflow-debugging-information
    '''

    try:
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
        os.environ['KERAS_BACKEND'] = 'plaidml.keras.backend'

        from tensorflow.python.platform.tf_logging import set_verbosity, ERROR
        from tensorflow.python.util import deprecation

        set_verbosity(ERROR)

        def deprecated(date, instructions, warn_once=True):
            def deprecated_wrapper(func):
                return func
            return deprecated_wrapper

        deprecation.deprecated = deprecated

    except ImportError:
        pass


def haversine(point1: tuple, point2: tuple, unit: Enum = Unit.KILOMETERS) -> float:

    """
    Calculate the great-circle distance between two points on the Earth surface.
    Takes two 2-tuples, containing the latitude and longitude of each point in decimal degrees,
    and, optionally, a unit of length.

    `point1`: first point; tuple of (latitude, longitude) in decimal degrees

    `point2`: second point; tuple of (latitude, longitude) in decimal degrees

    `unit`: a member of haversine.Unit, or, equivalently, a string containing the
    initials of its corresponding unit of measurement (i.e. miles = mi), default 'km' (kilometers).

    Example: `haversine((45.7597, 4.8422), (48.8567, 2.3508), unit=Unit.METERS)`
    Precondition: `unit` is a supported unit (supported units are listed in the `Unit` enum)

    Returns: the distance between the two points in the requested unit, as a float.
    The default returned unit is kilometers. The default unit can be changed by setting the unit
    parameter to a member of `haversine.Unit` (e.g. `haversine.Unit.INCHES`), or, equivalently,
    to a string containing the corresponding abbreviation (e.g. `'in'`).
    All available units can be found in the `Unit` enum.
    """

    lat1, lng1 = point1
    lat2, lng2 = point2

    lat1 = radians(lat1)
    lng1 = radians(lng1)
    lat2 = radians(lat2)
    lng2 = radians(lng2)

    lat = lat2 - lat1
    lng = lng2 - lng1
    d = sin(lat * 0.5) ** 2 + cos(lat1) * cos(lat2) * sin(lng * 0.5) ** 2

    return 2 * get_avg_earth_radius(unit) * asin(sqrt(d))


def haversine_vector(array1: list[tuple], array2: list[tuple],
                     unit: Enum = Unit.KILOMETERS) -> list[float]:

    '''
    The exact same function as "haversine", except that this
    version replaces math functions with numpy functions.
    This may make it slightly slower for computing the haversine
    distance between two points, but is much faster for computing
    the distance between two vectors of points due to vectorisation.
    '''

    try:
        import numpy as np

        if len(array1) != len(array2):
            raise ValueError('Input arrays have different lengths.'
                             f'Length of `array1` = {len(array1)}, length of `array2` = {len(array2)}')

        # ensure arrays are numpy ndarrays and iterable over rows
        array1 = np.expand_dims(array1, 0) if (array1 := np.array(array1)).ndim == 1 else np.array(array1)
        array2 = np.expand_dims(array2, 0) if (array2 := np.array(array2)).ndim == 1 else np.array(array2)

    except (ModuleNotFoundError, AttributeError):
        warnings.warn('Unable to import Numpy, using `haversine()` in a loop instead. \n'
                      'The `comb` parameter is not functional without numpy. \n'
                      'Try installing Numpy using $ pip install numpy.', ImportWarning)
        return [haversine(p1, p2, unit=unit) for p1, p2 in zip(array1, array2)]

    # unpack latitude/longitude
    lat1, lng1 = array1[:, 0], array1[:, 1]
    lat2, lng2 = array2[:, 0], array2[:, 1]

    # convert all latitudes/longitudes from decimal degrees to radians
    lat1 = np.radians(lat1)
    lng1 = np.radians(lng1)
    lat2 = np.radians(lat2)
    lng2 = np.radians(lng2)

    # calculate haversine
    lat = lat2 - lat1
    lng = lng2 - lng1
    d = (np.sin(lat * 0.5) ** 2
         + np.cos(lat1) * np.cos(lat2) * np.sin(lng * 0.5) ** 2)

    return 2 * get_avg_earth_radius(unit) * np.arcsin(np.sqrt(d))
