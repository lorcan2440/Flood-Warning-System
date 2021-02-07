# Copyright (C) 2018 Garth N. Wells
#
# SPDX-License-Identifier: MIT

"""
This module contains a collection of functions related to
geographical data.
"""

from .utils import sorted_by_key, wgs84_to_web_mercator
from .haversine import haversine_vector, Unit
from .station import MonitoringStation

from bokeh.plotting import figure, output_file, show
from bokeh.models import ColumnDataSource
from bokeh.tile_providers import CARTODBPOSITRON, get_provider


def stations_by_distance(stations: list, p: tuple):

    '''
    Returns a list of (station, distance) tuples, where
    station is a MonitoringStation object and distance
    is the float distance of that station from the given
    coordinate p.
    '''

    # Standard data type input checks
    assert isinstance(stations, list) and all([isinstance(i, MonitoringStation) for i in stations])
    assert isinstance(p, tuple)

    # preserve original order in case of other scripts running at the same time
    _stations = stations
    ref_points, station_points = [p for i in range(len(_stations))], [s.coord for s in _stations]

    # use haversine_vector to efficiently find the distance between multiple points
    my_data = zip(_stations, list(haversine_vector(ref_points, station_points, unit=Unit.KILOMETERS)))
    del _stations

    # sort by distance (second item in each list)
    return sorted_by_key(my_data, 1)


def stations_within_radius(stations: list, centre: tuple, r):

    '''
    Returns a list of all stations (type MonitoringStation)
    within radius r of a geographic coordinate centre.
    '''

    # standard data type input checks
    assert isinstance(r, float) or isinstance(r, int)

    # get all (station, distance) pairs
    sorted_stations = stations_by_distance(stations, centre)

    # return station where distance is <= the given radius
    return [s[0] for s in sorted_stations if s[1] <= r]


def rivers_with_station(stations: list):

    '''
    Returns a set of the names of all rivers which have
    a MonitoringStation instance associated with them.
    '''

    # Standard data type input checks
    assert all([isinstance(i, MonitoringStation) for i in stations])

    # Set (comprehension) to skip over/remove duplicates
    rivers = {station.river.strip() for station in stations}

    return rivers


def stations_by_river(stations: list):

    '''
    Returns a dict that maps river names to a list of
    station objects associated with that river.
    '''

    # Standard data type input checks
    assert all([isinstance(i, MonitoringStation) for i in stations])

    rivers = rivers_with_station(stations)

    # For each river listed, add all its associated stations.
    river_dict = {}
    for river in rivers:
        pair = {river: [station for station in stations if station.river == river]}
        river_dict.update(pair)

    return river_dict
     

def rivers_by_station_number(stations: list, N: int):

    '''
    Returns a list of (river name, number of stations)
    tuples. The tuples are sorted by number of stations,
    and only the top N values are included. Where several
    rivers have the same number of stations, all such
    rivers are included in the list.
    '''

    # Standard data type input and bounds checks
    assert all([isinstance(i, MonitoringStation) for i in stations])
    assert isinstance(N, int) and N >= 1

    river_names = rivers_with_station(stations)
    river_dict = stations_by_river(stations)

    # Get a complete list of (river name, number of stations) tuples,
    # sorted in decreasing order by number of stations
    river_num_list = sorted([(r, len(river_dict[r])) for r in river_names],
                            key=lambda x: x[1], reverse=True)

    # Find the number of stations which is N from the highest, accounting
    # for possible duplicates by removing them with the set constructor.
    end_num = sorted(list({r[1] for r in river_num_list}), reverse=True)[N - 1]

    # Starting from the river with the most stations and working down,
    # add the (river name, number of stations) tuple to the list until
    # the number of stations is less than the previously found limit
    rivers_list = []
    for (r, n) in river_num_list:
        if n >= end_num:
            rivers_list.append((r, n))
        else:
            break

    return rivers_list


def display_stations_on_map(stations, with_details=True, return_image=False):

    '''
    Shows a map of the stations across the UK. Uses Bokeh:
    https://docs.bokeh.org/en/latest/docs/user_guide/geo.html
    '''

    output_file("tile.html")
    tile_provider = get_provider(CARTODBPOSITRON)
    trans_coords = [wgs84_to_web_mercator(station.coord) for station in stations]

    # range bounds supplied in web mercator coordinates
    p = figure(x_range=(-1000000, 200000), y_range=(6250000, 8180000),
            x_axis_type="mercator", y_axis_type="mercator")  # noqa
    p.add_tile(tile_provider)

    source = ColumnDataSource(data=dict(
        lat             = [station.coord[0] for station in stations],       # noqa
        long            = [station.coord[1] for station in stations],       # noqa
        typical_range   = [station.typical_range for station in stations],  # noqa
        river           = [station.river for station in stations],          # noqa
        town            = [station.town for station in stations],           # noqa
        x_coord         = [x[0] for x in trans_coords],                     # noqa
        y_coord         = [x[1] for x in trans_coords])                     # noqa
    )                                                                       # noqa

    p.circle(x="x_coord", y="y_coord", size=15, fill_color="blue", fill_alpha=0.8, source=source)

    if with_details:
        from bokeh.models import HoverTool
        my_hover = HoverTool()
        my_hover.tooltips = [('Latitude', '@lat'), ('Longitude', '@long'),
                            ('Typical range', '@typical_range'), ('River', '@river'),
                            ('Town', '@town')]
        p.add_tools(my_hover)

    if return_image:
        return p
    else:
        show(p)
