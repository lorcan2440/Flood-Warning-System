"""
This module contains functions to produce maps.
"""

# built-in libraries

# external libraries
import pandas as pd
import plotly.graph_objects as go

# local imports


# Stamen map designs - base URLs
STAMEN_TERRAIN = "https://tiles.stadiamaps.com/styles/stamen_terrain.json"
STAMEN_TONER = "https://tiles.stadiamaps.com/styles/stamen_toner.json"
STAMEN_WATERCOLOR = "https://tiles.stadiamaps.com/styles/stamen_watercolor.json"


# NOTE: need to add "?api_key=YOUR-API-KEY" to the end


def stations_map_plotly(
    stations,
    filter_station_type: str | list[str] = None,
    map_design: str = STAMEN_TERRAIN,
    govuk_page_on_click: bool = False,
) -> go.Figure:
    """
    Create a map of the stations across England as a Plotly figure.
    Each station is represented by a coloured dot, with the colour indicating the relative water level.
    The user can hover over each dot to see more information about the station.

    #### Arguments

    `stations` (list[MonitoringStation]): a list of all input stations

    #### Optional Kwargs - for both backends

    `filter_station_type` (str | list[str], default = None): whether to show only stations of a specified type.
    Use "River Level", "Tidal", "Groundwater" or a list of these for multiple filters.
    If None, no filter is applied. If an empty list is passed, no stations will be shown.

    `map_design` (str, default = 'open-street-map'): the design of the map.
    - Docs: https://plotly.com/python/tile-map-layers/.
    - Stamen designs: https://tiles.stadiamaps.com/styles/stamen_toner.json?api_key=YOUR-API-KEY

    `show_map` (bool, default = False): whether to display the map in a new window.
    If False, the map will be returned as a Plotly figure. If True, the map will be displayed.

    `govuk_page_on_click` (bool, default = False): whether to open the station URL when the user
    clicks on one of the station points. This takes them to the station's page on the gov.uk website.

    #### Returns
    `fig` (go.Figure): the Plotly figure showing the map of stations.
    It can be included in a Dash app or shown on its own with `fig.show()`.
    """

    # Apply filtering if needed
    if filter_station_type:
        if isinstance(filter_station_type, str):
            stations = [s for s in stations if s.station_type == filter_station_type]
        elif isinstance(filter_station_type, (list, tuple, set)):
            stations = [s for s in stations if s.station_type in filter_station_type]

    # Define colour mappings
    COLOURS = {
        "red": "#fa0101",
        "orange": "#ff891e",
        "yellow": "#fff037",
        "light green": "#8ec529",
        "green": "#32a058",
        "grey": "#a2a2a2",
        "light blue": "#319fca",
        "blue": "#2636f4",
        "white": "#ffffff",
    }

    # Extract station data into a DataFrame
    data = []
    for s in stations:
        lat, lon = s.coord if s.coord else ("???", "???")
        level = s.latest_level if s.latest_level is not None else "???"
        typical_min, typical_max = (
            s.typical_range if s.typical_range else ("???", "???")
        )
        rel_level = (
            round(s.relative_water_level() * 100, 1)
            if s.relative_water_level() is not None
            else "???"
        )

        # Determine colour
        if rel_level != "???":
            if rel_level < 50:
                dot_col = "green"
            elif rel_level < 100:
                dot_col = "light green"
            elif rel_level < 175:
                dot_col = "yellow"
            elif rel_level < 250:
                dot_col = "orange"
            else:
                dot_col = "red"
        else:
            dot_col = "blue" if s.station_type == "Tidal" else "grey"

        data.append(
            [
                lat,
                lon,
                s.name,
                level,
                typical_min,
                typical_max,
                rel_level,
                s.river,
                s.town,
                s.station_type,
                s.url,
                COLOURS[dot_col],
            ]
        )

    df = pd.DataFrame(
        data,
        columns=[
            "lat",
            "lon",
            "name",
            "level",
            "typical_min",
            "typical_max",
            "rel_level",
            "river",
            "town",
            "station_type",
            "url",
            "color",
        ],
    )

    # Create the Plotly figure
    fig = go.Figure(
        go.Scattermapbox(
            lat=df["lat"],
            lon=df["lon"],
            mode="markers",
            marker=dict(size=7, color=df["color"]),
            hoverinfo="text",
            text=df.apply(
                lambda row: f"<b>Station:</b> {row['name']}<br>"
                f"<b>Current Level:</b> {row['level']} m<br>"
                f"<b>Typical Range:</b> {row['typical_min']} - {row['typical_max']} m<br>"
                f"<b>Relative Level:</b> {row['rel_level']}%<br>"
                f"<b>Type:</b> {row['station_type']}<br>"
                f"<b>River:</b> {row['river']}<br>"
                f"<b>Town:</b> {row['town']}<br>"
                f"<b>Coords:</b> ({row['lat']}°N, {row['lon']}°E)",
                axis=1,
            ),
            customdata=df["url"],  # Stores URLs for click events
        )
    )

    # Layout settings
    fig.update_layout(
        autosize=True,
        hovermode="closest",
        hoverdistance=5,
        width=1000,
        height=600,
        mapbox=dict(
            bearing=0, center=dict(lat=53, lon=-3), pitch=0, zoom=5, style=map_design
        ),
        margin=dict(l=0, r=0, t=1, b=0),
    )

    return fig
