import copy
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import pandas_market_calendars as mcal
import ta
import yfinance as yf
from sklearn.preprocessing import MinMaxScaler, StandardScaler


def calculate_natural_days_for_business_days(end_date, business_days) -> int:
    """Calcula el número de días naturales necesarios para obtener una cantidad
    específica de días hábiles hacia atrás desde una fecha de fin dada.

    Args:
        end_date (datetime): Fecha de fin.
        business_days (int): Número de días hábiles.

    Returns:
        int: Número de días naturales.
    """
    nyse = mcal.get_calendar("NYSE")
    count = 0
    delta_days = 0
    while count < business_days:
        check_date = end_date - pd.DateOffset(days=delta_days)
        if check_date in nyse.valid_days(start_date=check_date, end_date=end_date):
            count += 1
        delta_days += 1

    return delta_days


class StockData:
    """
    Clase para la obtención, procesamiento y transformación de datos financieros
    de múltiples activos, incluyendo indicadores técnicos y diversas formas de retorno.
    """

    def __init__(
        self,
        comp_abv: list,
        comp_names: list,
        difference_start_end: int = 5,
        end_date: datetime = datetime.now(),
        start_date: datetime = None,
        features: list = ["Close", "High", "Low", "Open"],
        include_cash: bool = False,
        winsorize: bool = True,
        percentile: float = 0.001,
        technical_indicators: list = [
            "SMA",
            "EMA",
            "RSI",
            "MACD",
            "Bollinger_High",
            "Bollinger_Low",
            "ATR",
        ],
    ):
        """
        Inicializa la clase con los datos de mercado y sus indicadores técnicos.

        Args:

            comp_abv (list): Lista de siglas de las compañías.
            comp_names (list): Lista de nombres de las compañías.
            difference_start_end (int): Diferencia entre la fecha de inicio y fin en años.
            end_date (datetime): Fecha de fin de los datos.
            start_date (datetime): Fecha de inicio de los datos.
            features (list): Lista de características a incluir.
            include_cash (bool): Si se debe incluir un activo de efectivo.
            winsorize (bool): Si se debe aplicar winsorización a los datos.
            percentile (float): Percentil para la winsorización.
            technical_indicators (list): Lista de indicadores técnicos a incluir.
        """
        assert not (end_date is None and start_date is not None), (
            "If start date is specified, end_date must be specified as well."
        )

        self.comp_abv = comp_abv
        self.comp_names = comp_names
        self.end_date = end_date
        self.start_date = start_date or datetime(
            end_date.year - difference_start_end, end_date.month, end_date.day
        )

        self.features = features
        self.include_cash = include_cash
        self.winsorize = winsorize
        self.percentile = percentile
        self.technical_indicators = technical_indicators

        self._get_stock_data()
        self._get_relative_return_data()
        self._get_relative_return_normalized()

    def _include_tech_indicators(self, df, ticker) -> pd.DataFrame:
        """Agrega indicadores técnicos al DataFrame del activo.

        Args:
            df (pd.DataFrame): DataFrame con los datos del activo.
            ticker (str): Nombre o sigla del activo.

        Returns:
            pd.DataFrame: DataFrame con los indicadores técnicos agregados.
        """
        indicators = {}
        close, high, low = (
            df[("Close", ticker)],
            df[("High", ticker)],
            df[("Low", ticker)],
        )

        for ind in self.technical_indicators:
            if ind == "SMA":
                value = ta.trend.sma_indicator(close, window=20)
            elif ind == "EMA":
                value = ta.trend.ema_indicator(close, window=20)
            elif ind == "RSI":
                value = ta.momentum.rsi(close)
            elif ind == "MACD":
                value = ta.trend.macd(close)
            elif ind == "Bollinger_High":
                value = ta.volatility.bollinger_hband(close)
            elif ind == "Bollinger_Low":
                value = ta.volatility.bollinger_lband(close)
            elif ind == "ATR":
                value = ta.volatility.average_true_range(high, low, close)

            indicators[(ind, ticker)] = value

        ind_df = pd.DataFrame(indicators, index=df.index)
        return pd.concat([df, ind_df], axis=1)

    def _get_stock_data(self):
        """Descarga y estructura los datos de mercado y sus indicadores técnicos."""
        dict_np = {}
        df_list = []
        extra_days = int(100 * 1.5)
        days_to_remove = 50

        smallest_size = float("inf")

        for stock in self.comp_abv:
            data = yf.download(
                stock,
                self.start_date - pd.DateOffset(days=extra_days),
                self.end_date,
                timeout=30,
                # auto_adjust=False,
                threads=False,
            )
            data = self._include_tech_indicators(data, stock)
            data = data[days_to_remove:]

            if data.isnull().values.any():
                print(f"Missing values in {stock}")

            df_list.append(data.assign(Stock=stock))
            data_numpy = data[self.features + self.technical_indicators].to_numpy()
            if data_numpy.shape[0] < smallest_size:
                smallest_size = data_numpy.shape[0]

            dict_np[stock] = data_numpy

        N = smallest_size
        stock_data = np.stack(
            [dict_np[stock][:N, :] for stock in self.comp_abv], axis=1
        )

        self.stock_data_numpy = stock_data
        self.stock_data_df = pd.concat(df_list)

        multi_index = pd.MultiIndex.from_product(
            [self.comp_abv, self.features + self.technical_indicators],
            names=["Stock", "Feature"],
        )
        idx = self.stock_data_df.index[:N]

        reshaped = stock_data.reshape(N, -1)
        self.multi_index_df = pd.DataFrame(reshaped, index=idx, columns=multi_index)

    def get_min_max_normalization(self) -> pd.DataFrame:
        """Devuelve los datos normalizados usando MinMaxScaler."""
        scaler = MinMaxScaler()
        return self.stock_data_df.groupby("Stock").apply(
            lambda x: scaler.fit_transform(x)
        )

    def _get_relative_return_data(self):
        """Calcula retornos simple, logarítmico y bruto de los precios."""
        shape = self.stock_data_numpy.shape
        gross = np.ones(shape)
        simple = np.zeros(shape)
        log = np.zeros(shape)

        for t in range(1, shape[0]):
            curr = self.stock_data_numpy[t, :, : len(self.features)]
            prev = self.stock_data_numpy[t - 1, :, : len(self.features)]
            ratio = np.divide(curr, prev)
            gross[t, :, : len(self.features)] = ratio
            simple[t, :, : len(self.features)] = ratio - 1
            log[t, :, : len(self.features)] = np.log(ratio)

        for arr in (gross, simple, log):
            arr[:, :, len(self.features) :] = self.stock_data_numpy[
                :, :, len(self.features) :
            ]

        if self.include_cash:
            cash = np.ones((shape[0], 1, shape[2]))
            gross = np.concatenate([cash, gross], axis=1)
            simple = np.concatenate([cash, simple], axis=1)
            log = np.concatenate([cash, log], axis=1)

        self.gross_return_data_numpy = gross
        self.simple_return_data_numpy = simple
        self.log_return_data_numpy = log

    def _get_relative_return_normalized(self):
        """Genera versiones normalizadas de los retornos usando diversas técnicas."""
        self.original_data_min_max = self._min_max_normalization(self.stock_data_numpy)
        self.original_data_standard = self._standard_scaler(self.stock_data_numpy)
        self.simple_return_data_normalized_min_max = self._min_max_normalization(
            self.simple_return_data_numpy
        )
        self.log_return_data_normalized_min_max = self._min_max_normalization(
            self.log_return_data_numpy
        )
        self.gross_return_data_normalized_min_max = self._min_max_normalization(
            self.gross_return_data_numpy
        )

        self.simple_return_data_normalized_standard = self._standard_scaler(
            self.simple_return_data_numpy
        )
        self.log_return_data_normalized_standard = self._standard_scaler(
            self.log_return_data_numpy
        )
        self.gross_return_data_normalized_standard = self._standard_scaler(
            self.gross_return_data_numpy
        )

        self.simple_return_data_winsorized = self._winsorize_transform(
            self.simple_return_data_numpy
        )
        self.log_return_data_winsorized = self._winsorize_transform(
            self.log_return_data_numpy
        )
        self.gross_return_data_winsorized = self._winsorize_transform(
            self.gross_return_data_numpy
        )

    def _min_max_normalization(self, data_np) -> np.ndarray:
        """Normaliza los datos usando un MinMaxScaler."""
        scaler = MinMaxScaler()
        data = data_np.copy()
        for i in range(data.shape[2]):
            if self.winsorize:
                data[:, :, i] = self._winsorize(data[:, :, i])
            data[:, :, i] = scaler.fit_transform(data[:, :, i])
        return data

    def _standard_scaler(self, data_np) -> np.ndarray:
        """Normaliza los datos usando un StandardScaler."""
        scaler = StandardScaler()
        data = data_np.copy()
        for i in range(data.shape[2]):
            if self.winsorize:
                data[:, :, i] = self._winsorize(data[:, :, i])
            data[:, :, i] = scaler.fit_transform(data[:, :, i])
        return data

    def _winsorize_transform(self, data_np) -> np.ndarray:
        """Aplica winsorización a los datos."""
        data = data_np.copy()
        for i in range(data.shape[2]):
            data[:, :, i] = self._winsorize(data[:, :, i])
        return data

    def _winsorize(self, data_np) -> np.ndarray:
        """Aplica winsorización a los datos."""
        lower = np.percentile(data_np, self.percentile * 100)
        upper = np.percentile(data_np, (1 - self.percentile) * 100)
        return np.clip(data_np, lower, upper)

    def extract_return_data_as_df(
        self, return_type="simple", normalized=None
    ) -> pd.DataFrame:
        """Extrae los retornos como DataFrame, normalizados o sin normalizar.
        Args:
            return_type (str): Tipo de retorno a extraer: 'simple', 'log' o 'gross'.
            normalized (str): Tipo de normalización: 'min_max', 'standard' o 'winsorized'.
        Returns:
            pd.DataFrame: DataFrame con los retornos de cada activo.

        """
        assert return_type in [None, "simple", "log", "gross"], "Invalid return type"

        lookup = {
            ("simple", None): self.simple_return_data_numpy,
            ("log", None): self.log_return_data_numpy,
            ("gross", None): self.gross_return_data_numpy,
            ("simple", "min_max"): self.simple_return_data_normalized_min_max,
            ("log", "min_max"): self.log_return_data_normalized_min_max,
            ("gross", "min_max"): self.gross_return_data_normalized_min_max,
            ("simple", "standard"): self.simple_return_data_normalized_standard,
            ("log", "standard"): self.log_return_data_normalized_standard,
            ("gross", "standard"): self.gross_return_data_normalized_standard,
            ("simple", "winsorized"): self.simple_return_data_winsorized,
            ("log", "winsorized"): self.log_return_data_winsorized,
            ("gross", "winsorized"): self.gross_return_data_winsorized,
            (None, None): self.stock_data_numpy,
            (None, "min_max"): self.original_data_min_max,
            (None, "standard"): self.original_data_standard,
        }

        data_np = lookup.get((return_type, normalized))
        if data_np is None:
            raise ValueError("Invalid return_type or normalization")

        companies = ["Cash"] + self.comp_abv if self.include_cash else self.comp_abv
        columns = self.features + self.technical_indicators
        dates = self.multi_index_df.index.get_level_values("Date")

        dfs = []
        for i, stock in enumerate(companies):
            df = pd.DataFrame(data_np[:, i, :], columns=columns, index=dates)
            df["Stock"] = stock
            dfs.append(df)

        full_df = pd.concat(dfs)
        full_df.index.name = "Date"
        return full_df

    def get_grouped_company_df(self):
        """Devuelve un DataFrame agrupado por compañía."""
        return self.stock_data_df.groupby("Stock")

    def calculate_portfolio_value(
        self, weights_dictionary, last_recorded_date, portfolio_value
    ):
        """Calcula los nuevos pesos de un portafolio en función del cambio en los precios.

        Args:
            weights_dictionary (dict): Pesos originales de inversión por activo.
            last_recorded_date (datetime): Última fecha de actualización del portafolio.
            portfolio_value (float): Valor total del portafolio en la fecha anterior.

        Returns:
            tuple: (nuevo valor total del portafolio, nuevos pesos, valores anteriores, nuevos valores)
        """
        new_values = {}
        previous_values = {}
        total_value = 0

        for stock, weight in weights_dictionary.items():
            stock_data = self.multi_index_df[stock]

            # Obtener precio anterior (último antes o en la fecha)
            if last_recorded_date in stock_data.index:
                previous_price = stock_data["Close"].loc[last_recorded_date]
            else:
                previous_price = stock_data["Close"].loc[:last_recorded_date].iloc[-1]

            # Precio actual
            current_price = stock_data["Close"].iloc[-1]

            # Valor anterior basado en el valor total del portafolio
            previous_stock_value = float(weight) * float(portfolio_value)
            previous_values[stock] = previous_stock_value

            # Valor actualizado (ajustado al cambio de precio)
            updated_value = previous_stock_value * (current_price / previous_price)
            new_values[stock] = updated_value
            total_value += updated_value

        # Nuevos pesos normalizados
        new_weights = {
            stock: value / total_value for stock, value in new_values.items()
        }

        return total_value, new_weights, previous_values, new_values


class DataGenerator:
    """
    Proveedor de datos para cada nuevo episodio en el entorno de entrenamiento.

    Genera secuencias temporales de datos financieros (observaciones) que incluyen
    una ventana de observación y los precios de cierre y apertura relevantes para simular operaciones.

    Atributos:
        history_np (np.ndarray): Datos históricos originales con shape (time, assets, features).
        normalized_np (np.ndarray): Versión normalizada de los datos históricos.
        steps (int): Número de pasos (días) simulados por episodio.
        window_length (int): Longitud de la ventana de observación.
        include_cash (bool): Si se incluye el activo de efectivo (cash) como parte del portafolio.
        feature_index (int): Índice de la feature que representa el precio de cierre.
    """

    def __init__(
        self,
        history_np,
        dates,
        abbreviation,
        normalized_np=None,
        steps=200,
        window_length=50,
        include_cash=False,
        feature_index=0,
    ):
        """
        Inicializa el generador de datos.

        Args:
            history_np (np.ndarray): Datos históricos. Shape: (time, assets, features)
            dates (list): Lista de pandas.Timestamp que representan los índices temporales.
            abbreviation (list): Nombres o siglas de los activos.
            normalized_np (np.ndarray, optional): Versión normalizada de los datos. Si no se provee, se usan los originales.
            steps (int): Número de pasos simulados por episodio.
            window_length (int): Tamaño de la ventana de observación.
            include_cash (bool): Si se debe incluir un activo de efectivo.
            feature_index (int): Índice de la feature para precios de cierre.
        """
        self.reset_pointer = 0
        self.step = 0
        self.steps = steps
        self.window_length = window_length
        self.include_cash = include_cash
        self.feature_index = feature_index

        self.num_stock = len(abbreviation) + 1 if include_cash else len(abbreviation)
        self.num_feature = int(history_np.shape[2])

        self._start_date = dates[0].date()
        self._dates = dates.copy()  # Fechas completas (inmutables)
        self.asset_names = copy.copy(abbreviation)

        self._data_np = history_np.copy()
        self._normalized_np = (
            normalized_np.copy() if normalized_np is not None else history_np.copy()
        )

        # Datos mutables por episodio
        self.dates = self._dates.copy()
        self.data_np = self._data_np.copy()
        self.normalized_np = self._normalized_np.copy()
        self.start_date = self._start_date

        # Inicia con una fecha un poco después para evitar bordes al principio
        initial_start = self.start_date + timedelta(days=int(self.window_length * 1.5))
        self.reset(initial_start)

    def _step(self) -> tuple[np.ndarray, np.ndarray, np.ndarray, bool]:
        """
        Avanza un paso en el episodio y devuelve:
            - La ventana de observación (normalized)
            - Precios de cierre actuales
            - Precios de apertura del día siguiente
            - Indicador de si el episodio ha terminado

        Returns:
            obs (np.ndarray): Observación (window_length, assets, features)
            close1 (np.ndarray): Precios de cierre actuales
            open2 (np.ndarray): Precios de apertura del día siguiente
            done (bool): Fin del episodio
        """
        obs = self.normalized_np[self.step : self.step + self.window_length].copy()

        close1 = self.data_np[
            self.step + self.window_length - 1 : self.step + self.window_length,
            :,
            self.feature_index,
        ].copy()

        open2 = self.data_np[
            self.step + self.window_length : self.step + self.window_length + 1,
            :,
            0,
        ].copy()

        self.step += 1
        done = self.step >= self.steps - 1

        return obs, close1, open2, done

    def reset(self, start_date=None) -> np.ndarray:
        """
        Reinicia el generador de datos para un nuevo episodio.

        Si se proporciona `start_date`, se fuerza a comenzar desde esa fecha.
        Si no, se selecciona aleatoriamente un punto de inicio válido.

        Args:
            start_date (datetime.date, optional): Fecha desde la cual iniciar el episodio.

        Returns:
            obs (np.ndarray): Primera observación del nuevo episodio.
        """
        self.step = 0
        self.reset_pointer += 1

        if start_date is not None:
            self.idx = 0  # Comienza desde el principio

            if self.idx + self.steps + self.window_length > self._data_np.shape[0]:
                raise ValueError(
                    "La fecha de inicio es demasiado cercana al final del dataset."
                )

            self.start_date = start_date
        else:
            self.idx = np.random.randint(
                low=0,
                high=self._data_np.shape[0] - self.steps - self.window_length - 1,
            )
            self.start_date = self._dates[self.idx + self.window_length].date()

        self.dates = self._dates[
            self.idx + self.window_length : self.idx + self.window_length + self.steps
        ]

        self.data_np = self._data_np[
            self.idx : self.idx + self.steps + self.window_length
        ]

        self.normalized_np = self._normalized_np[
            self.idx : self.idx + self.steps + self.window_length
        ]

        assert self.data_np.shape[0] >= self.steps, (
            "Fecha de inicio inválida: debe permitir espacio suficiente para window_length + steps."
        )

        obs = self.normalized_np[0 : self.window_length].copy()

        return obs
