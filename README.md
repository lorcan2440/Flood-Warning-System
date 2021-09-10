# Flood Warning System

An API and demo frontend for monitoring flood likelihood in England, UK. Built to extend the Part IA Lent Term computing activity at CUED. Run the files in the `tasks` directory to see the standard functionality,
or by using

`$ ./runtasks.sh`

The tasks are documented at https://cued-partia-flood-warning.readthedocs.io/.

## Map Plotting

View the map by running `MapViewer.py` inside the `applications` directory i.e. `python applications/MapViewer.py`.

![CI](https://github.com/lorcan2440/Flood-Warning-System/actions/workflows/main.yml/badge.svg)

Map of stations across England:

<img src="https://user-images.githubusercontent.com/72615977/131227267-7c14cf48-8f9c-413f-8c3d-8b599b79ca19.png" height="500", alt="map">

Hover over a dot to view basic info:

<img src="https://user-images.githubusercontent.com/72615977/132128831-922c51d7-3f87-400f-ad07-5310ff156d34.png" height="500", alt="hover>

Click on a dot to go to the official [gov.uk](https://check-for-flooding.service.gov.uk/) site for the station:

<img src="https://user-images.githubusercontent.com/72615977/132128882-a61aa746-bdf4-44dc-884d-14a836fbb2ed.png" height="500", alt="gov.uk site>

## Forecasting

View some forecasts by running `LevelPredictions.py` inside the `applications` directory i.e. `python applications/LevelPredictions.py`. Forecasting can be done at each station by training and predicting from an LSTM (long short-term memory) RNN (recurrent neural network). Training and evaluation is done with `tensorflow` and `scikit-learn`.

<img src="https://user-images.githubusercontent.com/72615977/132906986-a25ff2aa-a9e6-41b2-936b-67c660eeca23.png" height="500" alt="forecast">

## Installing

Currently this is not available on PyPI. Instead, you can go [here](https://download-directory.github.io/) and download the `floodsystem` module at https://github.com/lorcan2440/Flood-Warning-System/tree/main/floodsystem. Name the zipped folder `floodsystem.zip`. Extract the floodsystem module to the directory of your program.

## Usage

Various uses of the API are given in the `tasks` folder. To get started,

```
from floodsystem.stationdata import build_station_list, update_water_levels

stations = build_station_list()
update_water_levels(stations)
```

Pass in `stations` to the API functions to see the results, e.g.

```
from floodsystem.flood import stations_level_over_threshold
print(stations_level_over_threshold(stations))
```
