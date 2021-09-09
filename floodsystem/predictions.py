import datetime
import os

import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, LSTM

from .datafetcher import fetch_measure_levels
from .station import MonitoringStation

os.environ["KERAS_BACKEND"] = "plaidml.keras.backend"
scalar = MinMaxScaler(feature_range=(0, 1))


def data_prep(data: list, lookback: int, exclude_latest: int = 0):

    """
    Function that prepares the dataset by constructing x, y pairs.
    Each y is determined on the previous `lookback` data points (x).

    Args:
        data (array): The water level data.
        lookback (int): The look back value, i.e. every y is determined how many x.
        exclude (int, optional): The number of latest data points to ignore (default 0).

    Returns:
        array: x.
        array: y.
    """

    if exclude_latest != 0:
        data = data[:-1 * exclude_latest]

    scaled_levels = scalar.transform(data.reshape(-1, 1))
    x = np.array([scaled_levels[i - lookback:i, 0] for i in range(lookback, len(scaled_levels))])
    x = np.reshape(x, (x.shape[0], 1, x.shape[1]))  # samples, time steps, features
    y = np.array([scaled_levels[i, 0] for i in range(lookback, len(scaled_levels))])

    return x, y


def build_model(lookback):

    """
    Function that builds the recurrent neural network, which has 1 lstm layer and 2 dense layers.

    Args:
        lookback (int): The look back value, which determines the input shape.

    Returns:
        Keras model: Untrained model.
    """

    model = Sequential()
    model.add(LSTM(256, activation='relu', input_shape=(1, lookback), recurrent_dropout=0.1))
    model.add(Dense(512, activation='relu'))
    # model.add(Dense(256, activation='relu'))
    model.add(Dense(1, activation='tanh'))
    model.compile(optimizer='adam', loss='mse')

    return model


def train_model(model, x, y, batch_size, epoch,
                save_file='./cache/models/predictor_model.hdf5', show_loss=False):
    """
    Function that trains and saves the Keras model.

    Args:
        model (Keras model): The built model.
        x (list): x.
        y (list): y.
        batch_size (int): Batch size.
        epoch (int): Number of epochs.
        save_file (str, optional): Path to save the trained model file
            (default: './cache/predictor_model.hdf5')
        show_loss (bool, optional): Whether to display the loss-epoch graph after training.

    Returns:
        Keras model: The trained model.
    """

    history = model.fit(x, y, batch_size=batch_size, epochs=epoch, verbose=1)
    if show_loss:
        plt.plot(history.history['loss'])
        plt.ylabel('loss')
        plt.show()

    try:
        model.save(save_file)
    except OSError:
        os.mkdir('./cache/models')
        model.save(save_file)

    return model


def train_all(stations: list[MonitoringStation],
        dataset_size=1000, lookback=2000, batch_size=256, epoch=20):

    """
    Function that trains models for all stations supplied.

    Args:
        stations (list): List of MonitoringStation objects.
        dataset_size (int, optional): The number of days in the dataset (default: 1000).
        lookback (int, optional): Look back value (default: 2000).
        batch_size (int, optional): (default: 256).
        epoch (int, optional): (default: 20).
    """

    for i, station in enumerate(stations):
        print(f'Training for {station.name} ({i}/{len(stations)})')
        levels = np.array(fetch_measure_levels(station.measure_id, datetime.timedelta(dataset_size))[1])
        scalar.fit(levels.reshape(-1, 1))  # fit the scalar on across the entire dataset
        x_train, y_train = data_prep(levels, lookback)
        train_model(build_model(lookback), x_train, y_train, batch_size, epoch,
                    save_file=f'./cache/models/{station.name}.hdf5')


def predict(station: MonitoringStation,
        dataset_size=1000, lookback=2000, iteration=100, display=300, use_pretrained=True,
        batch_size=256, epoch=20):

    """
    Function that predict a specified number of future water levels of a specific station.
    If the model for that station is not cached, it will be trained according to the parameters specified.

    The returned data includes actual data over the specified interval,
    demonstration data the model produced based on actual data points prior to the displayed actual data,
    and the predicted date using all the available actual data.

    Args:
        station_name (str): The name of the station.
        dataset_size (int, optional): The number of days in the dataset (default: 1000).
        lookback (int, optional): Look back value (default: 2000).
        iteration (int, optional): Number of future water levels to be predicted
            (effectively the number of times data in passed to the nn) (default: 100).
        display (int, optional): Number of real data points to be returned (default: 300).
        use_pretrained (bool, optional): Whether to used pretrained model if possible (default: True).
        batch_size (int, optional): (default: 256).
        epoch (int, optional): (default: 20).

    Returns:
        tuple:

        * 2-tuple (list, list)
          List of datetime objects of actual and demo data,
          list of datatime objects of future predicted data.
        * 3-tuple (list, list, list)
          Lists of water levels of actual data, demo data, predicted data.
    """

    station_name = station.name
    date, levels = fetch_measure_levels(station.measure_id, datetime.timedelta(dataset_size))
    date, levels = np.array(date), np.array(levels)
    scalar.fit(levels.reshape(-1, 1))  # fit the scalar on across the entire dataset

    if use_pretrained:
        try:
            model = load_model(f'./cache/models/{station_name}.hdf5')
        except Exception:
            print(f'No pre-trained model for {station_name} found, training a model for it now.')
            x_train, y_train = data_prep(levels, lookback)
            model = train_model(build_model(lookback), x_train, y_train, batch_size, epoch,
                                save_file=f'./cache/models{station_name}.hdf5')
    else:
        print(f'Training a model for {station_name} now.')
        x_train, y_train = data_prep(levels, lookback)
        model = train_model(build_model(lookback), x_train, y_train, batch_size, epoch,
                            save_file=f'./cache/models{station_name}.hdf5')

    # prediction of future `iteration` readings, based on the last `lookback` values
    predictions = None
    pred_levels = scalar.transform(levels[-lookback:].reshape(-1, 1))
    pred_levels = pred_levels.reshape(1, 1, lookback)
    for _ in range(iteration):
        prediction = model.predict(pred_levels)
        pred_levels = np.append(pred_levels[:, :, -lookback + 1:], prediction.reshape(1, 1, 1), axis=2)
        predictions = np.append(predictions, prediction, axis=0) if predictions is not None else prediction

    # demo of prediction of the last `display` data points,
    # which is based on the `lookback` values before the final 100 points
    demo = None
    demo_levels = scalar.transform(
        levels[-display - lookback:-display].reshape(-1, 1)).reshape(1, 1, lookback)
    for _ in range(display):
        prediction = model.predict(demo_levels)
        demo_levels = np.append(demo_levels[:, :, -lookback + 1:], prediction.reshape(1, 1, 1), axis=2)
        demo = np.append(demo, prediction, axis=0) if demo is not None else prediction

    # return on last <display> data points, the demo values, and future predictions
    date = (date[-display:], [date[-1] + datetime.timedelta(minutes=15) * i for i in range(iteration)])
    return date, (levels[-display:], scalar.inverse_transform(
        demo).ravel(), scalar.inverse_transform(predictions).ravel())
