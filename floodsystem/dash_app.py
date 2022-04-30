'''
This module provides the functions for creating the Dash
dashboard web application.

Reference:
https://dash.plotly.com/
'''

import requests
import time
import multiprocessing as mp

import plotly.express as px
from plotly.graph_objects import FigureWidget, Scatter
from dash import Dash, Input, Output, dcc, html, callback_context
import dash_bootstrap_components as dbc
from flask import request

try:
    from .stationdata import build_station_list, update_water_levels
    from .stationdata import build_rainfall_gauge_list, update_rainfall_levels
    from .map import stations_map_plotly
    from .utils import patch_multiprocessing_pickler
except ImportError:
    from stationdata import build_station_list, update_water_levels
    from stationdata import build_rainfall_gauge_list, update_rainfall_levels
    from map import stations_map_plotly
    from utils import patch_multiprocessing_pickler


patch_multiprocessing_pickler()
app = Dash(__name__, external_stylesheets=[dbc.themes.SLATE], prevent_initial_callbacks=True)
if 'stations' not in globals():
    stations = build_station_list()
    gauges = build_rainfall_gauge_list()
    update_water_levels(stations)
    update_rainfall_levels(gauges)

# handle requests to shut down server
@app.server.route('/shutdown', methods=['POST'])
def shutdown():
    def shutdown_server():
        # NOTE: this may be depreciated: https://github.com/pallets/werkzeug/issues/1752
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()

    shutdown_server()
    return 'Server shutting down...'


def run_with_timeout(app: Dash, timeout: float, host='127.0.0.1', port=8050, debug=False):

    SHUTDOWN_URL = 'http://' + host + ':' + str(port) + '/shutdown'

    p1 = mp.Process(target=app.run_server, kwargs={'host': host, 'port': port, 'debug': debug})
    p2 = mp.Process(target=requests.post, args=(SHUTDOWN_URL,))

    p1.start()
    time.sleep(timeout)
    print(f'Terminating process because script called with argument {timeout} seconds.')
    p2.start()


# draw bar chart sample
def draw_sample_graph_figure(width=450, height=375, className='graph-object', html_only: bool = False):

    df = px.data.iris()

    if html_only:
        return dcc.Graph(
            figure=px.bar(df, x="sepal_width", y="sepal_length", color="species").update_layout(
                template='plotly_dark', plot_bgcolor='rgba(0, 0, 0, 0)', paper_bgcolor='rgba(0, 0, 0, 0)',
                width=width, height=height),
            className=className, config={'displayModeBar': False},
        )
    else:
        return html.Div([dbc.Card(dbc.CardBody([
            dcc.Graph(
                figure=px.bar(df, x="sepal_width", y="sepal_length", color="species").update_layout(
                    template='plotly_dark', plot_bgcolor='rgba(0, 0, 0, 0)', paper_bgcolor='rgba(0, 0, 0, 0)',
                    width=width, height=height),
                className=className, config={'displayModeBar': False},
            )]))])


@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def render_page_content(pathname):

    PAGE_LOOKUP = {
        '/': home_page_content,
        '/stations': stations_page_content,
        '/rainfall': rainfall_page_content,
        '/forecasts': forecasts_page_content,
        '/warnings': warnings_page_content
    }

    try:
        return PAGE_LOOKUP[pathname]

    except KeyError:

        # if the user tries to reach a different page, return a 404 message
        return dbc.Jumbotron(
            [
                html.H1('404: Not found', className='text-danger'),
                html.Hr(),
                html.P(f'The page name {pathname} was not recognised...'),
            ]
        )


#########################
#   Webpage Components  #
#########################

# heading card with text
header_card = dbc.Row([dbc.Col([html.Div([dbc.Card(dbc.CardBody([html.Div([
    html.H2('Flood Warning System'),
    html.H6('A web app for monitoring flood likelihood in England, UK')],
    style={'textAlign': 'center'})]))])], width=12)], class_name='header')

# side bar
sidebar = html.Div(
    [
        html.H4('Options'),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink('Home', href='/', active='exact'),
                dbc.NavLink('River Levels', href='/stations', active='exact'),
                dbc.NavLink('Rainfall', href='/rainfall', active='exact'),
                dbc.NavLink('Forecasts', href='/forecasts', active='exact'),
                dbc.NavLink('Flood Warnings', href='/warnings', active='exact'),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    className='sidebar'
)

# content for each page

content = html.Div(id='page-content', className='page-content')

home_page_content = html.Div([
    html.P("This is the content of the home page!"),
    draw_sample_graph_figure()])

stations_page_content = dbc.Col([
    dcc.Graph(figure=stations_map_plotly(stations), className='graph-object'),
    draw_sample_graph_figure(width=300, html_only=True)])

rainfall_page_content = html.Div([
    html.P("View rainfall data here."),
    draw_sample_graph_figure()])

forecasts_page_content = html.Div([
    html.P("Forecasts on this page."),
    draw_sample_graph_figure()]
)

warnings_page_content = html.Div([
    html.P("Beware of floods here!"),
    draw_sample_graph_figure()]
)

app.title = 'Flood Warning System'

# define app layout
app.layout = html.Div([dbc.Card(dbc.CardBody(
    [
        dcc.Location(id='url'),
        header_card,
        sidebar,
        content,
    ]),
    color='dark')]
)


if __name__ == '__main__':
    app.run_server(port=8888, debug=True)
