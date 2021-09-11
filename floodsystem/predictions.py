import datetime
import os

import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler

from .datafetcher import fetch_measure_levels
from .station import MonitoringStation

RESOURCES = os.path.join(os.path.dirname(__file__), 'resources')
PROPLOT_STYLE_SHEET = os.path.join(RESOURCES, 'proplot_style.mplstyle')

scalar = MinMaxScaler(feature_range=(0, 1))

try:
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    os.environ['KERAS_BACKEND'] = 'plaidml.keras.backend'

    # noinspection PyPackageRequirements
    import tensorflow as tf
    from tensorflow.python.util import deprecation

    tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)

    def deprecated(date, instructions, warn_once=True):  # pylint: disable=unused-argument
        def deprecated_wrapper(func):
            return func
        return deprecated_wrapper

    deprecation.deprecated = deprecated

    from tensorflow.keras.models import Sequential, load_model
    from tensorflow.keras.layers import Dense, LSTM

except ImportError:
    pass


def data_prep(data: np.ndarray, lookback: int,
        exclude_latest: int = 0) -> tuple[np.ndarray, np.ndarray]:

    """
    Prepares dataset by constructing x, y pairs. Each y is determined on the previous
    `lookback` data points (x).

    Args:
        data (array): The water level data.
        lookback (int): The look back value, i.e. every y is determined how many x.
        exclude (int, optional): The number of latest data points to ignore (default 0).

    Returns arrays (x, y).
    """

    if exclude_latest != 0:
        data = data[:-1 * exclude_latest]

    scaled_levels = scalar.transform(data.reshape(-1, 1))
    x = np.array([scaled_levels[i - lookback:i, 0] for i in range(lookback, len(scaled_levels))])
    x = np.reshape(x, (x.shape[0], 1, x.shape[1]))  # samples, time steps, features
    y = np.array([scaled_levels[i, 0] for i in range(lookback, len(scaled_levels))])

    return x, y


def build_model(lookback: int, **kwargs) -> Sequential:

    """
    Builds the RNN, which has 1 LSTM layer and 2 dense layers.

    ### Input

    #### Required

    `lookback` (int): The look back value, which determines the input shape.

    #### Optional

    `layer_units` (tuple[int], default = (256, 512, 1)): number of neurons in each layer
    `layer_activations` (tuple[str], default = ('relu', 'relu', 'tanh')): activation functions for each layer
    `recurrent_dropout` (float, default = 0.1): fraction of the units to drop for the linear
    transformation of the recurrent state. First layer only.
    `optimizer` (str, default = 'Adam): apply an optimiser when compiling the model.
    `loss` (str, default = 'mean_squared_error'): choose a loss function for the model.

    #### Returns

    `tensorflow.keras.model.Sequential` model: untrained Keras model.
    """

    layer_units = kwargs.get('layer_units', (256, 512, 1))
    layer_activations = kwargs.get('layer_activations', ('relu', 'relu', 'tanh'))
    recurrent_dropout = kwargs.get('recurrent_dropout', 0.1)
    optimizer = kwargs.get('optimizer', 'Adam')
    loss = kwargs.get('loss', 'mean_squared_error')

    model = Sequential()

    model.add(LSTM(layer_units[0], activation=layer_activations[0],
        input_shape=(1, lookback), recurrent_dropout=recurrent_dropout))
    model.add(Dense(layer_units[1], activation=layer_activations[1]))
    model.add(Dense(layer_units[2], activation=layer_activations[2]))
    model.compile(optimizer=optimizer, loss=loss)

    return model


def train_model(model: Sequential, x: list, y: list, batch_size: int, epoch: int, **kwargs) -> Sequential:

    """
    Trains and saves the Keras model.

    ### Inputs

    #### Required

    `model` (Keras model): the built model to train.
    `x` (list): x, the known input levels.
    `y` (list): y, the known levels after the input.
    `batch_size` (int, default = 256): number of samples processed before the model parameters are updated.
    `epoch` (int, default = 20): number of times to work through the full dataset.

    #### Optional

    `save_file` (str, default = './cache/predictor_model.hdf5'): Path to save the trained model file
    `show_loss` (bool, default = False): whether to display the loss-epoch graph after training.
    `verbose` (int, default = 0): verbosity of trainer, how much info is showed as training progresses.

    ### Returns

    `tensorflow.keras.model.Sequential` model: the trained model.
    """
    if kwargs.get('save_file', None) is not None:
        model_name = kwargs['save_file'].split("/")[-1].split('.')[0]
    else:
        model_name = 'predictor_model'

    save_file = kwargs.get('save_file', './cache/models/predictor_model.hdf5')
    show_loss = kwargs.get('show_loss', False)
    verbose = kwargs.get('verbose', 0)

    history = model.fit(x, y, batch_size=batch_size, epochs=epoch, verbose=verbose)
    end_loss = history.history['loss'][-1]

    loss_color = '#1ec888' if end_loss < 0.001 else \
                 '#e19124' if end_loss < 0.005 else \
                 '#e8401c'

    if show_loss:
        loss_name = model.loss.replace('_', ' ').title()
        plt.style.use(PROPLOT_STYLE_SHEET)
        plt.title(f'Loss convergence of training for {model_name}')
        plt.plot(np.arange(1, epoch + 1), history.history['loss'],
            label='loss', color='#58308f')
        plt.plot((1, epoch), (end_loss, end_loss),
            label=f'converged on {end_loss}', color=loss_color, linestyle='dashed')
        plt.legend()
        plt.xlabel(f'Epoch number (batch size {batch_size}), out of {epoch}')
        plt.ylabel(f'Loss ({loss_name})')
        plt.show()

    try:
        model.save(save_file)
    except OSError:
        os.mkdir('./cache/models')
        model.save(save_file)

    return model


def train_all(stations: list[MonitoringStation], dataset_size: int = 1000, lookback: int = 2000,
        batch_size: int = 256, epoch: int = 20, **kwargs) -> dict[MonitoringStation, Sequential]:

    """
    Trains and saves models for all stations supplied.

    ### Inputs

    #### Required

    `stations` (list): list of `MonitoringStation` objects.

    #### Optional

    `dataset_size` (int, default = 1000): the number of days in the dataset.
    `lookback` (int, default = 2000): look back value.
    `batch_size` (int, default = 256): number of samples processed before the model parameters are updated.
    `epoch` (int, default = 20): number of times to work through the full dataset.
    `show_loss` (bool, default = False): whether to display the loss-epoch graph after training.
    `layer_units` (tuple[int], default = (256, 512, 1)): number of neurons in each layer
    `layer_activations` (tuple[str], default = ('relu', 'relu', 'tanh')): activation functions for each layer
    `recurrent_dropout` (float, default = 0.1): fraction of the units to drop for the linear
    transformation of the recurrent state. First layer only.
    `optimizer` (str, default = 'Adam): apply an optimiser when compiling the model.
    `loss` (str, default = 'mean_squared_error'): choose a loss function for the model.

    ### Returns

    `dict[MonitoringStation, tensorflow.keras.models.Sequential]`: a mapping from each given station
    to its trained model.
    """

    trained_models = []

    for i, station in enumerate(stations):
        print(f'Training for {station.name} ({i}/{len(stations)})')
        levels = np.array(fetch_measure_levels(station, datetime.timedelta(dataset_size))[1])
        scalar.fit(levels.reshape(-1, 1))  # fit the scalar on across the entire dataset
        x_train, y_train = data_prep(levels, lookback)
        model = build_model(lookback, **kwargs)
        train_model(model, x_train, y_train, batch_size, epoch,
                    save_file=f'./cache/models/{station.name}.hdf5', **kwargs)
        trained_models.append(model)

    return dict(zip(stations, trained_models))


def predict(station: MonitoringStation, dataset_size: int = 1000, lookback: int = 2000,
        iteration: int = 100, display: int = 300, use_pretrained: bool = True, batch_size: int = 256,
        epoch: int = 20, del_model_after: bool = False) -> tuple[tuple[list, list, list], tuple[list, list]]:

    """
    Predicts a specified number of future water levels of a specific station.
    If the model for that station is not cached, it will be trained according to the parameters specified.

    The returned data includes actual data over the specified interval, demonstration data the model
    produced based on actual data points prior to the displayed actual data, and the predicted date
    using all the available actual data.

    The prediction can be graphed using `plot_predicted_water_levels(s, *predict(s))`, where `s` is
    a `MonitoringStation` after importing the plot function from `floodsystem.plot`.

    ### Inputs

    #### Required

    `station_name` (str): The name of the station.

    #### Optional

    `dataset_size` (int, default = 1000): the number of days in the dataset.
    `lookback` (int, default = 2000): look back value.
    `iteration` (int, default = 100): number of future 15-minute-interval water levels to predict.
    `display` (int, default = 300): number of real data points to be returned.
    `use_pretrained` (bool, default = True): whether to used pretrained model if possible.
    `batch_size` (int, default = 256): number of samples processed before the model parameters are updated.
    `epoch` (int, default = 20): number of times to work through the full dataset.

    ### Returns

    #### First item

    `(list[datetime.datetime], list[datetime.datetime])`: first list contains all dates up to the present,
    second list contains dates in future which have been predicted.

    #### Second item

    `(list[float], list[float], list[float])`: first list is actual level data, second list is the
    level data predicted using past data and third list is future level data predicted using current data.
    """

    station_name = station.name
    date, levels = fetch_measure_levels(station, datetime.timedelta(dataset_size))
    date, levels = np.array(date), np.array(levels)
    scalar.fit(levels.reshape(-1, 1))  # fit the scalar on across the entire dataset

    if use_pretrained:
        try:
            model = load_model(f'./cache/models/{station_name}.hdf5')
        except (ImportError, OSError):
            print(f'No pre-trained model for {station_name} found, training a model for it now.')
            x_train, y_train = data_prep(levels, lookback)
            model = train_model(build_model(lookback), x_train, y_train, batch_size, epoch,
                                save_file=f'./cache/models/{station_name}.hdf5')
    else:
        print(f'Training a model for {station_name} now.')
        x_train, y_train = data_prep(levels, lookback)
        model = train_model(build_model(lookback), x_train, y_train, batch_size, epoch,
                            save_file=f'./cache/models/{station_name}.hdf5')

    # prediction of future `iteration` readings, based on the last `lookback` values
    predictions = None
    pred_levels = scalar.transform(levels[-lookback:].reshape(-1, 1))
    pred_levels = pred_levels.reshape(1, 1, lookback)
    for _ in range(iteration):
        prediction = model.predict(pred_levels)
        pred_levels = np.append(pred_levels[:, :, -lookback + 1:], prediction.reshape(1, 1, 1), axis=2)
        predictions = np.append(predictions, prediction, axis=0) if predictions is not None else prediction

    # demo of prediction of the last `display` data points,
    # which is based on the `lookback` values before the final `iteration` points
    demo = None
    demo_levels = scalar.transform(
        levels[-display - lookback:-display].reshape(-1, 1)).reshape(1, 1, lookback)
    for _ in range(display):
        prediction = model.predict(demo_levels)
        demo_levels = np.append(demo_levels[:, :, -lookback + 1:], prediction.reshape(1, 1, 1), axis=2)
        demo = np.append(demo, prediction, axis=0) if demo is not None else prediction

    # option to delete model to save disk/drive space
    if del_model_after:
        os.remove(f'./cache/models/{station_name}.hdf5')

    # return on last `display` data points, the demo values, and future predictions
    date = (date[-display:], [date[-1] + datetime.timedelta(minutes=15) * i for i in range(iteration)])
    return date, (levels[-display:], scalar.inverse_transform(
        demo).ravel(), scalar.inverse_transform(predictions).ravel())
