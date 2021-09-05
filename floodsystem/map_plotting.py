'''
This module contains functions to produce maps.
'''

# pylint: disable=relative-beyond-top-level, no-name-in-module

from .utils import wgs84_to_web_mercator

from bokeh.plotting import figure, output_file, show
from bokeh.models import ColumnDataSource, OpenURL, TapTool, HoverTool
from bokeh.tile_providers import STAMEN_TERRAIN_RETINA, get_provider


def display_stations_on_map(stations: list, return_image: bool = False) -> None:

    '''
    Shows a map of the stations across England by running a HTML file in a browser.

    Uses Bokeh:
    https://docs.bokeh.org/en/latest/docs/user_guide/geo.html
    '''

    # inputs and outputs
    map_range = ((59, -12), (49, 4))  # (lat, long) coords of the map boundary
    output_file("England Stations Map.html", title='Flood Monitoring Stations Across England')

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

    # choose a map design: http://docs.bokeh.org/en/1.3.2/docs/reference/tile_providers.html
    tile_provider = get_provider(STAMEN_TERRAIN_RETINA)

    # setup
    w = wgs84_to_web_mercator
    letter = lambda lat, long: ('N' if lat >= 0 else 'S', 'E' if long >= 0 else 'W')  # noqa

    # colours: # https://docs.bokeh.org/en/latest/docs/reference/colors.html
    colors = ["#fa0101", "#ff891e", "#fff037", "#8ec529", "#32a058", "#a2a2a2"]
    linecolors = ["#9c3838", "#9e7d47", "#acac51", "#32a058", "#297231", "#6a6a6a"]
    trans_coords = [w(place["coords"]) for place in station_info]
    x_range, y_range = (w(map_range[0])[0], w(map_range[1])[0]), (w(map_range[0])[1], w(map_range[1])[1])

    # define figure
    p = figure(x_range=x_range, y_range=y_range, x_axis_type="mercator", y_axis_type="mercator",
        tools=["tap", "pan", "wheel_zoom", "box_zoom", "save", "reset"])
    p.add_tile(tile_provider)

    # populate a CDS of the information in each place: list[tuple[*args]]
    info = [
        (*map(lambda c: abs(c), p["coords"]),                               # lat, long               # noqa
        *letter(*p["coords"]),                                              # ns, ew                  # noqa
        p["name"], p["current_level"],                                      # name, latest_level      # noqa
        p["typical_range"][0] if p["typical_range"] is not None else None,  # typical_range_min       # noqa
        p["typical_range"][1] if p["typical_range"] is not None else None,  # typical_range_max       # noqa
        str(round(p["relative_level"] * 100, 1)) + '%'                      # relative_level_percent  # noqa
            if p["relative_level"] is not None else None,                                             # noqa
        p["river"], p["town"], p['url'],                                    # river, town, url        # noqa
        colors[p["rating"]], linecolors[p["rating"]],                       # color, linecolor        # noqa
        x[0], x[1])                                                         # x_coord, y_coord        # noqa 
            for p, x in zip(station_info, trans_coords)                                               # noqa
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
                      ('Relative level', '@relative_level_percent'),
                      ('River', '@river'), ('Town', '@town'), ('Coords', '(@lat° @ns, @long° @ew)')]
    p.add_tools(hover)

    if return_image:
        return p
    else:
        show(p)
