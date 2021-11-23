import datetime
import os

import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler

from .datafetcher import fetch_measure_levels
from .station import MonitoringStation

RESOURCES = os.path.join(os.path.dirname(__file__), 'resources')
PROPLOT_STYLE_SHEET = os.path.join(RESOURCES, 'proplot_style.mplstyle')

try:
    # Disables initialisation warnings from tensorflow
    # https://stackoverflow.com/questions/35911252/disable-tensorflow-debugging-information
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    os.environ['KERAS_BACKEND'] = 'plaidml.keras.backend'

    from tensorflow.python.platform.tf_logging import set_verbosity, ERROR
    from tensorflow.python.util import deprecation

    set_verbosity(ERROR)

    def deprecated(date, instructions, warn_once=True):
        def deprecated_wrapper(func):
            return func
        return deprecated_wrapper

    deprecation.deprecated = deprecated

except ImportError:
    pass

from tensorflow.keras.models import Sequential, load_model  # noqa
from tensorflow.keras.layers import Dense, LSTM             # noqa
from tensorflow.python.keras.callbacks import History


def data_prep(data: np.ndarray, lookback: int, scaler: MinMaxScaler,
        exclude_latest: int = 0) -> tuple[np.ndarray, np.ndarray]:
    '''
    Prepares dataset by constructing x, y pairs. Each y is determined on the previous data points (x).

    #### Arguments

    `data` (np.ndarray): the water level data
    `lookback` (int): how long to look back for data
    `exclude_latest` (int, default = 0): the number of latest data points to ignore

    #### Returns

    tuple[np.ndarray, np.ndarray]: arrays x and y, respectively
    '''

    if exclude_latest != 0:
        data = data[:-1 * exclude_latest]

    scaled_levels = scaler.transform(data.reshape(-1, 1))
    x = np.array([scaled_levels[i - lookback:i, 0] for i in range(lookback, len(scaled_levels))])
    x = np.reshape(x, (x.shape[0], 1, x.shape[1]))  # samples, time steps, features
    y = np.array([scaled_levels[i, 0] for i in range(lookback, len(scaled_levels))])

    return x, y


def build_model(lookback: int, **kwargs) -> Sequential:
    '''
    Builds the RNN, which has 1 LSTM layer and 2 dense layers.

    #### Arguments

    `lookback` (int): determines the input shape

    #### Optional Args and Flags

    `layer_units` (tuple[int], default = (256, 512, 1)): number of neurons in each layer
    `layer_activations` (tuple[str], default = ('relu', 'relu', 'tanh')): activation functions for each layer
    `recurrent_dropout` (float, default = 0.1): fraction of the units to drop for the
    linear transformation of the recurrent state. First layer only
    `optimizer` (str, default = 'Adam'): apply an optimiser when compiling the model
    `loss` (str, default = 'mean_squared_error'): choose a loss function for the model

    #### Returns

    Sequential: untrained Keras model
    '''

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


def plot_model_loss(model: Sequential, model_name: str, history: History, use_logscale: bool = True,
        use_proplot_style: bool = True, batch_size: int = 'unspecified'):
    '''
    Shows a graph of the convergence of the loss for each epoch for a trained model.

    #### Arguments

    `model` (Sequential): model to test
    `model_name` (str): name of model
    `history` (History): loss values
    `use_logscale` (bool, default = True): whether to show loss on a log axis
    `use_proplot_style` (bool, default = True): use ProPlot stylesheet
    `batch_size` (int, default = 'unspecified'): batch size for displaying on graph
    '''

    epoch = len(history.history['loss'])
    end_loss = history.history['loss'][-1]
    loss_color = '#1ec888' if end_loss < 0.001 else \
                 '#e19124' if end_loss < 0.005 else \
                 '#e8401c'
    loss_name = model.loss.replace('_', ' ').title()

    if use_proplot_style:
        plt.style.use(PROPLOT_STYLE_SHEET)
    else:
        plt.style.use('default')

    plt.title(f'Loss convergence of training for {model_name}')
    plt.plot(np.arange(1, epoch + 1), history.history['loss'], label='loss', color='#58308f')
    plt.plot((1, epoch), (end_loss, end_loss),
        label=f'converged on {round(end_loss, 6)}', color=loss_color, linestyle='dashed')

    plt.legend()
    plt.xlabel(f'Epoch number (batch size {batch_size}), out of {epoch}')
    plt.ylabel(f'Loss ({loss_name})')
    if use_logscale:
        plt.yscale('log')

    plt.show()


def train_model(model: Sequential, x: list, y: list, batch_size: int, epoch: int, **kwargs) -> Sequential:
    '''
    Trains and saves the Keras model.

    #### Arguments

    `model` (Sequential): the built model to train
    `x` (list): the known input levels
    `y` (list): the known levels after the input
    `batch_size` (int, default = 256): number of samples processed before the model parameters are updated
    `epoch` (int, default = 20): number of times to work through the full dataset

    #### Optional

    `save_file` (str, default = './cache/predictor_model.hdf5'): path to save the trained model file
    `show_loss` (bool, default = False): whether to display the loss-epoch graph after training
    `use_proplot_style` (bool, default = True): whether to use the ProPlot style sheet if show_loss
    `verbose` (int, default = 0): verbosity of trainer, how much info is showed as training progresses

    #### Returns

    Sequential: the trained model
    '''

    if kwargs.get('save_file', None) is not None:
        model_name = kwargs['save_file'].split("/")[-1].split('.')[0]
    else:
        model_name = 'predictor_model'

    save_file = kwargs.get('save_file', './cache/models/predictor_model.hdf5')
    show_loss = kwargs.get('show_loss', False)
    verbose = kwargs.get('verbose', 0)
    use_proplot_style = kwargs.get('use_proplot_style', True)

    history = model.fit(x, y, batch_size=batch_size, epochs=epoch, verbose=verbose)
    end_loss = history.history['loss'][-1]

    loss_color = '#1ec888' if end_loss < 0.001 else \
                 '#e19124' if end_loss < 0.005 else \
                 '#e8401c'

    if show_loss:
        plot_model_loss(model, model_name, history, use_proplot_style=use_proplot_style)

    try:
        model.save(save_file)
    except OSError:
        os.mkdir('./cache/models')
        model.save(save_file)

    return model


def train_all(stations: list[MonitoringStation], dataset_size: int = 1000, lookback: int = 2000,
        batch_size: int = 256, epoch: int = 20, **kwargs) -> dict[MonitoringStation, Sequential]:
    '''
    Trains and saves models for all stations supplied.

    #### Arguments

    `stations` (list[MonitoringStation]): list of stations to generate models for
    `dataset_size` (int, default = 1000): the number of days in the dataset
    `lookback` (int, default = 2000): look back value
    `batch_size` (int, default = 256): number of samples processed before the model parameters are updated
    `epoch` (int, default = 20): number of times to work through the full dataset

    #### Optional Kwargs

    `show_loss` (bool, default = False): whether to display the loss-epoch graph after training.
    `layer_units` (tuple[int], default = (256, 512, 1)): number of neurons in each layer
    `layer_activations` (tuple[str], default = ('relu', 'relu', 'tanh')): activation functions for each layer
    `recurrent_dropout` (float, default = 0.1): fraction of the units to drop for the linear
    transformation of the recurrent state. First layer only.
    `optimizer` (str, default = 'Adam): apply an optimiser when compiling the model.
    `loss` (str, default = 'mean_squared_error'): choose a loss function for the model.

    #### Returns

    dict[MonitoringStation, Sequential]: a mapping from each given station to its trained model
    '''

    trained_models = []
    scaler = MinMaxScaler(feature_range=(0, 1))

    for i, station in enumerate(stations):
        print(f'Training for {station.name} ({i}/{len(stations)})')
        levels = np.array(fetch_measure_levels(station, datetime.timedelta(dataset_size))[1])
        scaler.fit(levels.reshape(-1, 1))
        x_train, y_train = data_prep(levels, lookback, scaler)
        model = build_model(lookback, **kwargs)
        train_model(model, x_train, y_train, batch_size, epoch,
                    save_file=f'./cache/models/{station.name}.hdf5', **kwargs)
        trained_models.append(model)

    return dict(zip(stations, trained_models))


def predict(station: MonitoringStation, dataset_size: int = 1000, lookback: int = 2000,
        iteration: int = 100, display: int = 300, use_pretrained: bool = True, batch_size: int = 256,
        epoch: int = 20, del_model_after: bool = False) -> tuple[tuple[list, list], tuple[list, list, list]]:
    '''
    Predicts a specified number of future water levels of a specific station.
    If the model for that station is not cached, it will be trained according to the parameters specified.

    The returned data includes actual data over the specified interval, demonstration data the model
    produced based on actual data points prior to the displayed actual data, and the predicted date
    using all the available actual data.

    The prediction can be graphed using `plot_predicted_water_levels(s, *predict(s))`, where `s` is
    a `MonitoringStation` after importing the plot function from `floodsystem.plot`.

    #### Arguments

    `station` (MonitoringStation): the station to predict the future levels for
    `dataset_size` (int, default = 1000): the number of days in the dataset
    `lookback` (int, default = 2000): look back value
    `iteration` (int, default = 100): number of future 15-minute-interval water levels to predict
    `display` (int, default = 300): number of real data points to be returned
    `use_pretrained` (bool, default = True): whether to used pretrained model if possible
    `batch_size` (int, default = 256): number of samples processed before the model parameters are updated
    `epoch` (int, default = 20): number of times to work through the full dataset
    `del_model_after` (bool, default = False): whether to delete the ~30 MB model file after predicting

    #### Returns

    tuple[tuple[list, list], tuple[list, list, list]]: first tuple contains all dates up to the present,
    all dates in the future, respectively; second tuple contains the actual, past predicted and future
    predicted levels, respectively
    '''

    station_name = station.name
    date, levels = fetch_measure_levels(station, datetime.timedelta(dataset_size))
    date, levels = np.array(date), np.array(levels)

    scaler = MinMaxScaler(feature_range=(0, 1))
    scaler.fit(levels.reshape(-1, 1))

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
    pred_levels = scaler.transform(levels[-lookback:].reshape(-1, 1))
    pred_levels = pred_levels.reshape(1, 1, lookback)
    for _ in range(iteration):
        prediction = model.predict(pred_levels)
        pred_levels = np.append(pred_levels[:, :, -lookback + 1:], prediction.reshape(1, 1, 1), axis=2)
        predictions = np.append(predictions, prediction, axis=0) if predictions is not None else prediction

    # demo of prediction of the last `display` data points,
    # which is based on the `lookback` values before the final `iteration` points
    demo = None
    demo_levels = scaler.transform(
        levels[-display - lookback:-display].reshape(-1, 1)).reshape(1, 1, lookback)
    for _ in range(display):
        prediction = model.predict(demo_levels)
        demo_levels = np.append(demo_levels[:, :, -lookback + 1:], prediction.reshape(1, 1, 1), axis=2)
        demo = np.append(demo, prediction, axis=0) if demo is not None else prediction

    # option to delete model to save disk/drive space
    if del_model_after:
        os.remove(f'./cache/models/{station_name}.hdf5')

    # return on last `display` data points, the demo values, and future predictions
    dates_to_now = date[-display:]
    dates_future = [date[-1] + datetime.timedelta(minutes=15) * i for i in range(iteration)]
    levels_to_now = levels[-display:]
    levels_past_predicted = scaler.inverse_transform(demo).ravel()
    levels_future_predicted = scaler.inverse_transform(predictions).ravel()
    return (dates_to_now, dates_future), (levels_to_now, levels_past_predicted, levels_future_predicted)
