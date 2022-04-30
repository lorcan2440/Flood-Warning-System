# built-in libraries
import datetime
import os

# third-party libraries
import numpy as np
from sklearn.preprocessing import MinMaxScaler

# local imports
try:
    from .datafetcher import fetch_measure_levels
    from .station import MonitoringStation
    from .plot import plot_model_loss, plot_predicted_water_levels
    from .utils import read_only_properties, hide_tensorflow_debug_logs
except ImportError:
    from datafetcher import fetch_measure_levels
    from station import MonitoringStation
    from plot import plot_model_loss, plot_predicted_water_levels
    from utils import read_only_properties, hide_tensorflow_debug_logs

RESOURCES = os.path.join(os.path.dirname(__file__), 'assets')
PROPLOT_STYLE_SHEET = os.path.join(RESOURCES, 'proplot_style.mplstyle')
__FORECAST_PROTECTED_ATTRS = ('station', 'dates_to_now', 'levels_to_now',
    'levels_past_predicted', 'dates_future', 'levels_future_predicted')

# stop tensorflow printing debug messages when imported
hide_tensorflow_debug_logs()

# third-party libraries
from tensorflow.keras.models import Sequential, load_model  # noqa
from tensorflow.keras.layers import Dense, LSTM  # noqa


@read_only_properties(*__FORECAST_PROTECTED_ATTRS)
class Forecast:

    '''
    Class containing information about an RNN-generated forecast for a station.

    NOTE: the attributes `station`, `dates_to_now`, `levels_to_now`, `levels_past_predicted`,
    `dates_future` and `levels_future_predicted` are read-only.

    #### Attributes

    `Forecast.dates_future` (list[datetime.datetime]): the dates into the future for which a forecast exists
    `Forecast.levels_future_predicted` (list[float]): the future forecasted water levels
    `Forecast.station` (floodsystem.station.MonitoringStation): the station which this forecast is for

    #### Optional Attributes

    These may or may not exist depending on the information passed into the `predict` function.

    `Forecast.dates_to_now` (list[datetime.datetime]): the dates in the past for which a forecast exists
    `Forecast.levels_to_now` (list[float]): the true recorded levels at each of Forecast.dates_to_now
    `Forecast.levels_past_predicted` (list[float]): the past forecasted water levels
    `Forecast.metadata` (dict): additional info about the forecast, including about the model used. Keys:
        {'has_past_forecast', 'dataset_size', 'lookback', 'iterations',
        'batch_size', 'used_pretrained', 'epochs'}

    #### Methods

    `Forecast.plot_forecast()`
    '''

    def __init__(self, **kwargs):

        metadata = kwargs.get('metadata', None)
        if metadata is not None:
            self.station = metadata.get('station', None)
        self.dates_future = kwargs.get('dates_future')
        self.levels_future_predicted = kwargs.get('levels_future_predicted')

        for attr, val in kwargs.items():
            if val is not None and not hasattr(self, attr):
                if attr != 'metadata':
                    setattr(self, attr, val)
                else:
                    # do not include station as already included in self.station
                    self.metadata = {k: v for k, v in val.items() if k != 'station'}

    def plot_forecast(self, **kwargs):

        '''
        Plots a graph of the forecasted water levels. Wrapper for
        `floodsystem.plot.plot_predicted_water_levels`, which all kwargs are passed to, as well as
        any optional attributes set at initialisation (representing info from a past forecast).

        #### Optional Keyword Arguments

        `format_dates` (bool, default = True): format dates neater
        `y_axis_from_zero` (bool, default = None): whether to start the y-axis from the zero level
        `use_proplot_style` (bool, default = True): use ProPlot stylesheet
        '''

        _required_attrs = ('station', 'dates_future', 'levels_future_predicted')
        required_vals = [getattr(self, attr) for attr in _required_attrs]
        plot_kwargs = {**kwargs, **{k: v for k, v in self.__dict__.items() if k not in _required_attrs}}
        plot_predicted_water_levels(*required_vals, **plot_kwargs)

    def get_forecast(self, chosen_date: datetime.datetime = None) -> dict[datetime.datetime, float]:

        '''
        Returns the forecast in simple {date: level} form.

        #### Optional Keyword Arguments

        `chosen_date` (datetime.datetime, default = None): if specified,
        return only the forecast at this date, as a single float.

        #### Returns

        dict[datetime.datetime, float]: a dict of each datetime where a forecast has been made
        and the predicted water level in metres (a prediction of `MonitoringStation.latest_level`)
        at that time. If `chosen_date` is given, return only the water level instead.
        '''

        future_data = dict(zip(self.dates_future, self.levels_future_predicted))
        return future_data if chosen_date is None else future_data[chosen_date]


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


def train_model(model: Sequential, x: list, y: list, batch_size: int = 256, epoch: int = 20,
        **kwargs) -> Sequential:
    '''
    Trains and saves the Keras model. Training a single model takes approximately
    15-20 seconds per station with the default arguments.

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

    history = model.fit(x, y, batch_size=batch_size, epochs=epoch, verbose=verbose).history['loss']
    loss_name = model.loss.replace('_', ' ').title().strip()

    if show_loss:
        plot_model_loss(history, loss_name, model_name,
            use_proplot_style=use_proplot_style, batch_size=batch_size)

    try:
        model.save(save_file)
    except OSError:
        os.mkdir('./cache/models')
        model.save(save_file)

    return model


def train_all(stations: list[MonitoringStation], dataset_size: int = 1000, lookback: int = 2000,
        batch_size: int = 256, epoch: int = 20, **kwargs) -> dict[MonitoringStation, Sequential]:
    '''
    Trains and saves models for all stations supplied. Training a single model takes approximately
    15-20 seconds per station with the default arguments.

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
    `optimizer` (str, default = 'Adam'): apply an optimiser when compiling the model.
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
        train_model(model, x_train, y_train, batch_size=batch_size, epoch=epoch,
                    save_file=f'./cache/models/{station.name}.hdf5', **kwargs)
        trained_models.append(model)

    return dict(zip(stations, trained_models))


def predict(station: MonitoringStation, dataset_size: int = 1000, lookback: int = 2000,
        iteration: int = 100, use_pretrained: bool = True, batch_size: int = 256, epoch: int = 20,
        get_past_forecast: bool = False, display: int = 300,
        del_model_after: bool = True) -> Forecast:
    '''
    Predicts a specified number of future water levels of a specific station.
    If the model for that station is not cached, it will be trained according to the parameters specified.

    The returned data includes actual data over the specified interval, past data the model
    produced based on actual data points prior to the displayed actual data, and the predicted data
    using some of the available actual data.

    The prediction can be graphed using (where `station` is a MonitoringStation):
    ```
    forecast = floodsystem.forecasts.predict(station)
    forecast.plot_forecast(y_axis_from_zero=not station.is_tidal)
    ```

    #### Arguments

    `station` (MonitoringStation): the station to predict the future levels for

    #### Optional Keyword Arguments

    `dataset_size` (int, default = 1000): the number of days to fetch past water levels from
        (1 day provides 96 readings, if the station is functioning correctly)
    `lookback` (int, default = 2000): number of past readings to base the next predicted value on
    `iteration` (int, default = 100): number of future water levels to predict
        (1 per 15 minutes into the future)
    `use_pretrained` (bool, default = True): whether to used pretrained model if possible
    `batch_size` (int, default = 256): number of samples processed before the model parameters are updated
    `epoch` (int, default = 20): number of times to work through the full dataset
    `get_past_forecast` (bool, default = False): whether to additionally get a forecast based on the levels
        from a given `display` points before the present. Helpful for estimating the accuracy of the forecast
        by comparing to the known levels over this time.
    `display` (int, default = 300): number of real data points to show if using `get_past_forecast`.
    `del_model_after` (bool, default = True): whether to delete the model .hdf5 file after predicting.
        Frees up disk space (29 MB per model with default parameters) if multiple models are being trained.

    #### Returns

    `Forecast`: an object with attributes containing the forecast and information relating to it.
    The forecasted levels are stored in `Forecast.levels_future_predicted` at dates given in
    `Forecast.dates_future`. See `help(floodsystem.forecasts.Forecast)` for more info.
    '''

    # Reference:
    # https://machinelearningmastery.com/time-series-prediction-lstm-recurrent-neural-networks-python-keras/

    station_name = station.name
    dates, levels = fetch_measure_levels(station, datetime.timedelta(dataset_size))
    dates, levels = np.array(dates), np.array(levels)

    scaler = MinMaxScaler(feature_range=(0, 1))
    scaler.fit(levels.reshape(-1, 1))

    if use_pretrained:
        try:
            model = load_model(f'./cache/models/{station_name}.hdf5')
        except (ImportError, OSError):
            print(f'No existing model for {station_name} found, training a new model for it now...')
            x_train, y_train = data_prep(levels, lookback)
            model = train_model(build_model(lookback), x_train, y_train, batch_size, epoch,
                                save_file=f'./cache/models/{station_name}.hdf5')
    else:
        print(f'Training a model for {station_name} now...')
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

    # prediction of the last `display` data points, which is based on the `lookback` values
    # before the final `iteration` points
    if get_past_forecast:
        past = None
        past_levels = scaler.transform(
            levels[-display - lookback:-display].reshape(-1, 1)).reshape(1, 1, lookback)
        for _ in range(display):
            prediction = model.predict(past_levels)
            past_levels = np.append(past_levels[:, :, -lookback + 1:], prediction.reshape(1, 1, 1), axis=2)
            past = np.append(past, prediction, axis=0) if past is not None else prediction

    # option to delete model to save disk/drive space
    if del_model_after:
        os.remove(f'./cache/models/{station_name}.hdf5')

    # return on last `display` data points, the past values, and future predictions
    dates_to_now = dates[-display:] if get_past_forecast else None
    levels_to_now = levels[-display:] if get_past_forecast else None
    levels_past_predicted = scaler.inverse_transform(past).ravel() if get_past_forecast else None
    dates_future = [dates[-1] + datetime.timedelta(minutes=15) * i for i in range(iteration)]
    levels_future_predicted = scaler.inverse_transform(predictions).ravel()

    return Forecast(**{
        'dates_to_now': dates_to_now,
        'dates_future': dates_future,
        'levels_to_now': levels_to_now,
        'levels_past_predicted': levels_past_predicted,
        'levels_future_predicted': levels_future_predicted,
        'metadata': {'has_past_forecast': get_past_forecast, 'station': station,
                     'dataset_size': dataset_size, 'lookback': lookback, 'iterations': iteration,
                     'batch_size': batch_size, 'used_pretrained': use_pretrained, 'epochs': epoch}
    })
