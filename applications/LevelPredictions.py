# pylint: disable=import-error

import import_helper  # noqa

from floodsystem.stationdata import build_station_list
from floodsystem.predictions import train_all, predict
from floodsystem.plot import plot_predicted_water_levels


def run():

    # get list of stations to predict
    stations = build_station_list()
    station_names_to_predict = ['Hayes Basin']
    stations_to_predict = [s for s in stations if s.name in station_names_to_predict]

    # train models for each station
    print(f'Training forecasting model for {station_names_to_predict}')
    train_all(stations_to_predict)
    print('Training finished.')

    # get predictions
    for s in stations_to_predict:
        print(f'Forecasting for {s.name}')
        plot_predicted_water_levels(s, *predict(s))


if __name__ == '__main__':
    run()
