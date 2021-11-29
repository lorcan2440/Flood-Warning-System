'''
This module contains functions to produce maps.
'''

# pylint: disable=relative-beyond-top-level, no-name-in-module

import os
from itertools import groupby

from bokeh.plotting import Figure, figure, output_file, show
from bokeh.models import ColumnDataSource, OpenURL, TapTool, HoverTool
from bokeh.tile_providers import Vendors, get_provider

from floodsystem.station import MonitoringStation

from .utils import wgs84_to_web_mercator, coord_letters


def display_stations_on_map(stations: list[MonitoringStation], **kwargs) -> Figure:
    '''
    Shows a map of the stations across England by running a HTML file in a browser.

    Uses Bokeh:
    https://docs.bokeh.org/en/latest/docs/user_guide/geo.html

    #### Arguments

    `stations` (list[MonitoringStation]): a list of all input stations

    #### Optional Kwargs

    `filter_station_type` (str | list[str], default = None): whether to show only stations of a specified type.
    Use "River Level", "Tidal", "Groundwater" or a list of these for multiple filters.
    If None, no filter is applied. If an empty list is passed, no stations will be shown.

    `map_design` (str, default = 'SATELLITE'): tile provider for Bokeh map. 'SATELLITE' is equivalent
    to superposing 'ESRI_IMAGERY' and 'STAMEN_TONER_LABELS'. See
    https://docs.bokeh.org/en/latest/docs/reference/tile_providers.html for the options.
    Passed to bokeh.tile_providers.Vendors enum.

    `return_image` (bool, default = False): return the Figure as the output from this function
    `output_file` (str, default = 'England Stations Map.html'): filename of HTML output file
    `filedir` (str, default = ''): directory to put HTML file in, relative or absolute
    `map_title` (str, default = 'Flood Monitoring Stations Across England'): title of tab opened
    `verbose` (bool, default = True): whether to provide a text output description of what the map is showing.

    #### Returns

    bokeh.plotting.Figure (optional): the figure used in the map, returned if `return_image`, else None
    '''

    # kwargs
    filter_station_type = kwargs.get('filter_station_type', None)
    map_design = kwargs.get('map_design', 'SATELLITE')
    return_image = kwargs.get('return_image', False)
    filename = kwargs.get('output_file', 'England Stations Map.html')
    filedir = kwargs.get('filedir', '')
    title = kwargs.get('map_title', 'Flood Monitoring Stations Across England')
    verbose = kwargs.get('verbose', True)

    # inputs and outputs
    MAP_RANGE = ((59, -12), (49, 4))
    output_file(os.path.join(filedir, filename), title=title)
    colors = ["#fa0101", "#ff891e", "#fff037", "#8ec529", "#32a058", "#a2a2a2"]
    linecolors = ["#9c3838", "#9e7d47", "#acac51", "#32a058", "#297231", "#6a6a6a"]
    trans_range = [wgs84_to_web_mercator(coord) for coord in MAP_RANGE]
    x_range, y_range = zip(*trans_range)

    p = figure(x_range=x_range, y_range=y_range, x_axis_type="mercator", y_axis_type="mercator",
        tools=["tap", "pan", "wheel_zoom", "box_zoom", "save", "reset"])

    # choose map design: https://docs.bokeh.org/en/latest/docs/reference/tile_providers.html
    if map_design.upper() == "SATELLITE":
        p.add_tile(get_provider(Vendors.ESRI_IMAGERY))
        p.add_tile(get_provider(Vendors.STAMEN_TONER_LABELS))
    else:
        p.add_tile(get_provider(getattr(Vendors, map_design.upper())))

    # filter input if needed
    if filter_station_type is not None:
        if isinstance(filter_station_type, str):
            stations = list(filter(lambda s: s.station_type == filter_station_type, stations))
        elif isinstance(filter_station_type, (list, tuple, set, dict)):
            stations = list(filter(lambda s: s.station_type in filter_station_type, stations))

    # populate a CDS of the information in each place: list[tuple[*args]]
    info_by_station = [(
        *(map(lambda c: abs(c), s.coord) if s.coord is not None else (None, None)),
        *(coord_letters(*s.coord) if s.coord is not None else (None, None)),
        s.name,
        (ll if ll > 0 or s.is_tidal else "≤ 0")
            if (ll := s.latest_level) is not None else None,       # noqa
        *(s.typical_range if s.typical_range is not None else (None, None)),
        round(lv * 100, 1) if (lv := s.relative_water_level()) is not None else None,
        s.river,
        s.town,
        s.station_type,
        s.url,
        colors[(rating := ((4 if lv < 0.5 else
                            3 if lv < 1 else
                            2 if lv < 1.75 else
                            1 if lv < 2.5 else
                            0) if lv is not None else -1))],
        linecolors[rating],
        *wgs84_to_web_mercator(s.coord)) for s in stations]

    source = ColumnDataSource(
        dict(zip(['lat', 'long', 'ns', 'ew',
            'name', 'current_level', 'typical_range_min', 'typical_range_max',
            'relative_level_percent', 'river', 'town', 'station_type', 'url',
            'color', 'linecolor', 'x_coord', 'y_coord'], zip(*info_by_station))))

    # add a circle to the map, referencing the colours in the ColumnDataSource
    p.circle(x="x_coord", y="y_coord", size=10,
             fill_color="color", line_color="linecolor",
             fill_alpha=0.75, hover_alpha=1.0, source=source)

    # clicking on a circle will open the official page for that station
    # NOTE: requires bokeh version >= 2.3.3: https://github.com/bokeh/bokeh/issues/11182
    taptool = p.select(type=TapTool)
    taptool.callback = OpenURL(url='@url')

    # initialise a HoverTool and add the necessary parameters to display when activated
    hover = HoverTool()
    hover.tooltips = [('Station', '@name'), ('Current level', '@current_level m'),
                      ('Typical range', 'min: @typical_range_min m, max: @typical_range_max m'),
                      ('Relative level', '@relative_level_percent %'), ('Type of station', '@station_type'),
                      ('River', '@river'), ('Town', '@town'), ('Coords', '(@lat° @ns, @long° @ew)')]
    p.add_tools(hover)

    # print output if needed
    if verbose:
        nums = {k: len(list(v)) for k, v in groupby(stations, key=lambda s: s.station_type)}

        print(f'Displaying {len(stations)} monitoring stations (of which {nums}) on the map. \n \n'
        '>>> \t Use the toolbar on the right to interact with the map e.g. zoom, pan, save. \n'
        '>>> \t Hover over a dot to view basic info about the station. \n'
        '>>> \t If a dot is grey, this means either the station is tidal (no typical range), or the latest level is unavailable. \n'        # noqa
        '>>> \t Click on a dot to view the graph of the level data on the official gov.uk site.')

    if return_image:
        return p
    else:
        show(p)
