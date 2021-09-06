# Flood Warning System

An API and demo frontend for monitoring flood likelihood in England, UK. Built to extend the Part IA Lent Term computing activity at CUED.

The tasks are documented at https://cued-partia-flood-warning.readthedocs.io/.

## Demo

View the map by running `MapViewer.py` or run the files in the `tasks` directory to see the standard functionality.

![CI](https://github.com/lorcan2440/Flood-Warning-System/actions/workflows/main.yml/badge.svg)

Map of stations across England:

![image](https://user-images.githubusercontent.com/72615977/131227267-7c14cf48-8f9c-413f-8c3d-8b599b79ca19.png)

Hover over a dot to view basic info:

![image](https://user-images.githubusercontent.com/72615977/132128831-922c51d7-3f87-400f-ad07-5310ff156d34.png)

Click on a dot to go to the official [gov.uk](https://check-for-flooding.service.gov.uk/) site for the station:

![image](https://user-images.githubusercontent.com/72615977/132128882-a61aa746-bdf4-44dc-884d-14a836fbb2ed.png)

## Usage

Various uses of the API are given in the `tasks` folder. To get started,

`from floodsystem.stationdata import build_station_list, update_water_levels`

`stations = build_station_list()`
`update_water_levels(stations)`

Pass in `stations` to the API functions to see the results, e.g.

`from floodsystem.flood import stations_level_over_threshold`
`print(stations_level_over_threshold(stations))`

