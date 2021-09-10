# pylint: disable=import-error

import import_helper  # noqa

import os
from datetime import datetime

from floodsystem.stationdata import build_station_list
from floodsystem.predictions import train_all, predict
from floodsystem.plot import plot_predicted_water_levels


def run():

    # get list of stations to predict
    stations = build_station_list()
    station_names_to_predict = ['Goole']
    stations_to_predict = [s for s in stations if s.name in station_names_to_predict]

    # do not retrain if a trained model was already made within the last 24 hours
    model_path = './cache/models'

    #model_recent = (datetime.fromtimestamp(os.path.getmtime(model_path)) - datetime.now()).days >= 1
    
    print(f'Training forecasting model for {station_names_to_predict}')
    train_all(stations_to_predict, show_loss=True, loss='mean_squared_error')
    print('Training finished.')

    '''
    # get predictions
    for s in stations_to_predict:
        print(f'Forecasting for {s.name}')
        plot_predicted_water_levels(s, *predict(s))
    '''


if __name__ == '__main__':
    run()
