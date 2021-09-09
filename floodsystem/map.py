'''
This module contains functions to produce maps.
'''

# pylint: disable=relative-beyond-top-level, no-name-in-module

from .utils import wgs84_to_web_mercator_vector, coord_letters, get_else_none

from bokeh.plotting import figure, output_file, show
from bokeh.models import ColumnDataSource, OpenURL, TapTool, HoverTool
from bokeh.tile_providers import Vendors, get_provider


def display_stations_on_map(stations: list, map_design: str = "SATELLITE", return_image: bool = False) -> None:

    '''
    Shows a map of the stations across England by running a HTML file in a browser.

    Uses Bokeh:
    https://docs.bokeh.org/en/latest/docs/user_guide/geo.html
    '''

    # inputs and outputs
    map_range = ((59, -12), (49, 4))  # (lat, long) coords of the map boundary
    output_file("applications/map/England Stations Map.html",
        title='Flood Monitoring Stations Across England')

    station_info = []
    for i, s in enumerate(stations):
        lv = s.relative_water_level()
        station_info.append(
            {"coords": s.coord if s.coord is not None else (0, 0),
            "name": s.name,
            "current_level": s.latest_level,
            "typical_range": s.typical_range,
            "relative_level": lv,
            "river": s.river,
            "town": s.town,
            "url": s.url})

        if s.latest_level is not None:
            if s.latest_level <= 0:
                station_info[i]["current_level"] = "≤ 0"

        if lv is not None:
            station_info[i]["rating"] = (0 if lv > 2.5 else    # red
                                         1 if lv > 1.75 else   # orange
                                         2 if lv > 1 else      # yellow
                                         3 if lv > 0.5 else    # light green
                                         4)                    # green
        else:
            station_info[i]["rating"] = -1  # unknown: data was invalid / nonexistent - grey

    # colours: # https://docs.bokeh.org/en/latest/docs/reference/colors.html
    colors = ["#fa0101", "#ff891e", "#fff037", "#8ec529", "#32a058", "#a2a2a2"]
    linecolors = ["#9c3838", "#9e7d47", "#acac51", "#32a058", "#297231", "#6a6a6a"]
    trans_coords = wgs84_to_web_mercator_vector([place["coords"] for place in station_info])
    trans_range = wgs84_to_web_mercator_vector(map_range)
    x_range, y_range = trans_range[:, 0], trans_range[:, 1]

    # choose map design: https://docs.bokeh.org/en/latest/docs/reference/tile_providers.html
    p = figure(x_range=x_range, y_range=y_range, x_axis_type="mercator", y_axis_type="mercator",
        tools=["tap", "pan", "wheel_zoom", "box_zoom", "save", "reset"])

    if map_design.upper() == "SATELLITE":
        p.add_tile(get_provider(Vendors.ESRI_IMAGERY))
        p.add_tile(get_provider(Vendors.STAMEN_TONER_LABELS))
    else:
        p.add_tile(get_provider(getattr(Vendors, map_design.upper())))

    # populate a CDS of the information in each place: list[tuple[*args]]
    info = [
        (*map(lambda c: abs(c), p["coords"]),                               # lat, long
        *coord_letters(*p["coords"]),                                       # ns, ew
        p["name"], p["current_level"],                                      # name, latest_level
        get_else_none(p["typical_range"], 0),                               # typical_range_min
        get_else_none(p["typical_range"], 1),                               # typical_range_max
        get_else_none(p["relative_level"], func=lambda x: round(x * 100, 1)),  # relative_level_percent
        p["river"], p["town"], p['url'],                                    # river, town, url
        colors[p["rating"]], linecolors[p["rating"]],                       # color, linecolor
        x[0], x[1])                                                         # x_coord, y_coord
        for p, x in zip(station_info, trans_coords)
    ]

    source = ColumnDataSource(
        {k: v for k, v in zip(['lat', 'long', 'ns', 'ew',
            'name', 'current_level', 'typical_range_min', 'typical_range_max',
            'relative_level_percent', 'river', 'town', 'url',
            'color', 'linecolor', 'x_coord', 'y_coord'], list(zip(*info)))})

    # add a circle to the map, referencing the colours in the ColumnDataSource
    p.circle(x="x_coord", y="y_coord", size=10,
             fill_color="color", line_color="linecolor",
             fill_alpha=0.75, hover_alpha=1, source=source)

    # clicking on a circle will open the official page for that station
    # NOTE: requires bokeh version >= 2.3.3: https://github.com/bokeh/bokeh/issues/11182
    taptool = p.select(type=TapTool)
    taptool.callback = OpenURL(url='@url')

    # initialise a HoverTool and add the necessary parameters to display when activated
    hover = HoverTool()
    hover.tooltips = [('Station', '@name'), ('Current level', '@current_level m'),
                      ('Typical range', 'min: @typical_range_min m, max: @typical_range_max m'),
                      ('Relative level', '@relative_level_percent %'),
                      ('River', '@river'), ('Town', '@town'), ('Coords', '(@lat° @ns, @long° @ew)')]
    p.add_tools(hover)

    if return_image:
        return p
    else:
        show(p)
