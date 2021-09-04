'''
Haversine calculator
Source: https://pypi.org/project/haversine/
Direct download (.tar.gz): https://files.pythonhosted.org/packages/20/3a/f96adec3c7b50e9483149b906636e08ab01dd54de3da2f70b2d4ab769bfa/haversine-2.3.0.tar.gz  # noqa
Version 2.3.0,
Sep 4, 2020
'''

import warnings
from math import radians, cos, sin, asin, sqrt
from enum import Enum


# mean earth radius - https://en.wikipedia.org/wiki/Earth_radius#Mean_radius
_AVG_EARTH_RADIUS_KM = 6371.0088


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


def get_avg_earth_radius(unit: Enum) -> float:

    """
    Returns the average radius of the Earth in the chosen units.
    """

    unit = Unit(unit)
    return _AVG_EARTH_RADIUS_KM * _CONVERSIONS[unit]


def haversine(point1: tuple, point2: tuple, unit: Enum = Unit.KILOMETERS) -> float:

    """
    Calculate the great-circle distance between two points on the Earth surface.
    Takes two 2-tuples, containing the latitude and longitude of each point in decimal degrees,
    and, optionally, a unit of length.

    point1: first point; tuple of (latitude, longitude) in decimal degrees

    point2: second point; tuple of (latitude, longitude) in decimal degrees

    unit: a member of haversine.Unit, or, equivalently, a string containing the
    initials of its corresponding unit of measurement (i.e. miles = mi), default 'km' (kilometers).

    Example: ``haversine((45.7597, 4.8422), (48.8567, 2.3508), unit=Unit.METERS)``
    Precondition: ``unit`` is a supported unit (supported units are listed in the `Unit` enum)

    Returns: the distance between the two points in the requested unit, as a float.
    The default returned unit is kilometers. The default unit can be changed by setting the unit
    parameter to a member of ``haversine.Unit`` (e.g. ``haversine.Unit.INCHES``), or, equivalently,
    to a string containing the corresponding abbreviation (e.g. 'in').
    All available units can be found in the ``Unit`` enum.
    """

    # unpack latitude/longitude
    lat1, lng1 = point1
    lat2, lng2 = point2

    # convert all latitudes/longitudes from decimal degrees to radians
    lat1 = radians(lat1)
    lng1 = radians(lng1)
    lat2 = radians(lat2)
    lng2 = radians(lng2)

    # calculate haversine
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
