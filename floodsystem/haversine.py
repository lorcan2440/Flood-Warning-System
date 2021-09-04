'''
Haversine calculator
Source: https://pypi.org/project/haversine/
Direct download (.tar.gz): https://files.pythonhosted.org/packages/20/3a/f96adec3c7b50e9483149b906636e08ab01dd54de3da2f70b2d4ab769bfa/haversine-2.3.0.tar.gz  # noqa
Version 2.3.0,
Sep 4, 2020
'''


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
                     unit: Enum = Unit.KILOMETERS, comb: bool = False) -> list[float]:

    '''
    The exact same function as "haversine", except that this
    version replaces math functions with numpy functions.
    This may make it slightly slower for computing the haversine
    distance between two points, but is much faster for computing
    the distance between two vectors of points due to vectorisation.
    '''

    try:
        import numpy as np
    except ModuleNotFoundError:
        return 'Error, unable to import Numpy,\
        consider using haversine instead of haversine_vector, or run \n\
        $ pip install numpy'

    # ensure arrays are numpy ndarrays
    if not isinstance(array1, np.ndarray):
        array1 = np.array(array1)
    if not isinstance(array2, np.ndarray):
        array2 = np.array(array2)

    # ensure will be able to iterate over rows by adding dimension if needed
    if array1.ndim == 1:
        array1 = np.expand_dims(array1, 0)
    if array2.ndim == 1:
        array2 = np.expand_dims(array2, 0)

    # Asserts that both arrays have same dimensions if not in combination mode
    if not comb:
        if array1.shape != array2.shape:
            raise IndexError("""When not in combination mode, arrays must be of same
                            size. If mode is required, use comb=True as argument.""")

    # unpack latitude/longitude
    lat1, lng1 = array1[:, 0], array1[:, 1]
    lat2, lng2 = array2[:, 0], array2[:, 1]

    # convert all latitudes/longitudes from decimal degrees to radians
    lat1 = np.radians(lat1)
    lng1 = np.radians(lng1)
    lat2 = np.radians(lat2)
    lng2 = np.radians(lng2)

    # If in combination mode, turn coordinates of array1 into column vectors for broadcasting
    if comb:
        lat1 = np.expand_dims(lat1, axis=0)
        lng1 = np.expand_dims(lng1, axis=0)
        lat2 = np.expand_dims(lat2, axis=1)
        lng2 = np.expand_dims(lng2, axis=1)

    # calculate haversine
    lat = lat2 - lat1
    lng = lng2 - lng1
    d = (np.sin(lat * 0.5) ** 2
         + np.cos(lat1) * np.cos(lat2) * np.sin(lng * 0.5) ** 2)

    return 2 * get_avg_earth_radius(unit) * np.arcsin(np.sqrt(d))
