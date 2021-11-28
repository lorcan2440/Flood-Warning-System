# pylint: disable=import-error

import import_helper  # noqa

from floodsystem.stationdata import build_station_list
from floodsystem.forecasts import train_all, predict
from floodsystem.plot import plot_predicted_water_levels


def run():

    # get list of stations to predict
    print('Building station list...')
    stations = build_station_list()
    station_names_to_predict = ['Darlington Faverdale']
    stations_to_predict = [s for s in stations if s.name in station_names_to_predict]

    print(f'Training forecasting model for {station_names_to_predict}...')
    train_all(stations_to_predict, show_loss=True)
    print('Training finished.')

    predictions = dict()

    # get predictions
    for s in stations_to_predict:
        print(f'Getting predictions for {s.name}...')
        predictions[s.name] = predict(s)

    # plot graphs
    for s in stations_to_predict:
        print(f'Plotting forecast for {s.name}.')
        plot_predicted_water_levels(s, *predictions[s.name], y_axis_from_zero=not s.is_tidal)


if __name__ == '__main__':
    run()
