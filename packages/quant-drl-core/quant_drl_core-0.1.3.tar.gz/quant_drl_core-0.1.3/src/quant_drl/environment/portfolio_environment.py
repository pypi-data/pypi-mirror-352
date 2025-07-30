import os
import sys

import gymnasium as gym
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from gymnasium import spaces

from quant_drl.data.stock_data import DataGenerator

eps = 1e-8


def sharpe(returns, eps=1e-10):
    return (np.mean(returns) + eps) / (np.std(returns) + eps)


def sharpe_from_list(historical_info_list, key="retorno_logaritmico"):
    returns = list(map(lambda x: x[key], historical_info_list))
    if len(returns) < 5:
        return 0
    return sharpe(returns)


def max_drawdown(returns):
    """Max drawdown"""
    log_r = np.log(1 + returns)
    log_cum_r = np.cumsum(log_r)
    r_box = log_cum_r.copy()
    for i in range(len(returns)):
        r_box[i] = log_cum_r[i] - np.max(log_cum_r[0:i])
    MD = 1 - np.exp(np.min(r_box))

    return MD


def update_weight(w0, r0):
    if sum(r0 * w0) != 0:
        dw0 = (r0 * w0) / sum(r0 * w0)
    else:
        dw0 = w0 * 0  # keep the size
    return dw0


def best_performance_stock(y):
    """
    y have form (1.1 , 1.2, 0.9, ...) which is the past return
    """
    loc = np.argmax(y)
    w = np.zeros(len(y))
    w[loc] = 1
    return w


def performance_rank(y):
    """
    return the rank of return, e.g. [1.1,1.3,0.9] -> [1,2,0] best performance give highest value

    """
    x = y.argsort()
    ranks = np.empty_like(x)
    ranks[x] = np.arange(len(y))
    return ranks


def multiindex_dataframe_to_numpy(data, index_name, shape):
    """
    change multiindex dataframe to numpy array

    """
    a = data[index_name[0]].to_numpy().reshape(shape)
    a = a.astype(np.float32)
    for i in index_name[1:]:
        b = data[i].to_numpy().reshape(shape)
        b = b.astype(np.float32)
        a = np.append(a, b, axis=0)
    return a


def sparsemax(z):
    z_sorted = np.sort(z)[::-1]
    z_cumsum = np.cumsum(z_sorted)
    k = np.arange(1, len(z) + 1)

    z_check = 1 + k * z_sorted > z_cumsum
    k_z = k[z_check][-1]
    tau = (z_cumsum[z_check][-1] - 1) / k_z

    return np.maximum(z - tau, 0)


class PortfolioSimulator:
    """
    Simulador de portafolio para entornos de aprendizaje por refuerzo.

    Calcula recompensas, costos de transacción y registra la evolución del portafolio
    a lo largo de los pasos del episodio.
    """

    def __init__(self, asset_names, steps=200, trading_cost=0.0025, p0=2000):
        """
        Inicializa el simulador del portafolio.

        Args:
            asset_names (list): Lista de activos (excluyendo el efectivo).
            steps (int): Número total de pasos a simular.
            trading_cost (float): Coste de transacción por cambio de pesos.
            p0 (float): Valor inicial del portafolio.
        """
        self.asset_names = asset_names
        self.cost = trading_cost
        self.steps = steps
        self._p0 = p0
        self.p0 = p0

        self.infos = []
        self.sum_rho1 = 0
        self.step = 0

    def _step(self, w1, w0, close1, open2):
        """
        Realiza un paso de simulación, actualiza el valor del portafolio y calcula la recompensa.

        Args:
            w1 (np.ndarray): Nuevos pesos del portafolio en t.
            w0 (np.ndarray): Pesos del portafolio anteriores (t-1).
            close1 (np.ndarray): Precios de cierre en t.
            open2 (np.ndarray): Precios de apertura en t+1.

        Returns:
            rho1 (float): Retorno logarítmico del portafolio en t.
            info (dict): Información detallada del paso.
            done (bool): True si el portafolio se queda sin valor.
        """
        self.step += 1

        # Agregar efectivo como primer activo (valor constante de 1)
        close1_cash = np.insert(close1, 0, 1.0)
        open2_cash = np.insert(open2, 0, 1.0)

        # Calcular el vector dw1 y el coste de transacción
        dw1 = (close1_cash * w0) / np.dot(close1_cash, w0)
        c = self.cost * np.abs(dw1[1:] - w1[1:]).sum()
        mu1 = 1 - c

        # Calcular valor del portafolio actualizado
        mu_y_w = mu1 * np.dot(open2_cash, w1)
        p1 = self.p0 * mu_y_w

        # Calcular retornos
        r1 = mu_y_w - 1
        eps = 1e-8
        rho1 = np.log(mu_y_w + eps)
        self.sum_rho1 += rho1

        recompensa_acumulada = self.sum_rho1 / self.step

        info = {
            "recompensa_acumulada": recompensa_acumulada,
            "retorno_simple": r1,
            "retorno_logaritmico": rho1,
            "valor_portafolio": p1,
            "coste": c,
        }

        self.infos.append(info)
        self.p0 = p1
        done = p1 == 0

        return rho1, info, done

    def reset(self):
        """
        Reinicia el simulador a su estado inicial.
        """
        self.p0 = self._p0
        self.infos = []
        self.sum_rho1 = 0
        self.step = 0


class PortfolioEnvironment(gym.Env):
    """
        Entorno de aprendizaje por refuerzo para la gestión de portafolios financieros.

        Permite simular episodios de trading con costos de transacción, observaciones en ventanas
    de tiempo, y diferentes tipos de recompensa (log, sharpe, etc.).
    """

    metadata = {"render.modes": ["human", "ansi"]}

    def __init__(
        self,
        history_np,
        history_multiindex_df,
        abbreviation,
        normalized_history_np=None,
        steps=100,
        trading_cost=0.0025,
        window_length=5,
        initial_capital=2000,
        feature_index=3,
        reward_type="log_reward",
        start_date=None,
        random_initialization=True,
    ):
        """
        Inicializa el entorno de aprendizaje por refuerzo.

        Args:

            history_np (np.ndarray): Datos históricos de precios y características.
            history_multiindex_df (pd.DataFrame): Datos históricos con índice múltiple.
            abbreviation (list): Lista de abreviaturas de activos.
            normalized_history_np (np.ndarray): Datos históricos normalizados.
            steps (int): Número total de pasos a simular.
            trading_cost (float): Coste de transacción por cambio de pesos.
            window_length (int): Longitud de la ventana de tiempo.
            initial_capital (float): Capital inicial del portafolio.
            feature_index (int): Índice de la característica a utilizar.
            reward_type (str): Tipo de recompensa a utilizar.
            start_date (str): Fecha de inicio de la simulación.
            random_initialization (bool): Inicialización aleatoria del portaf
        """
        super().__init__()

        self.window_length = window_length
        self.num_stocks = len(abbreviation)
        self.trading_cost = trading_cost
        self._data_df = history_multiindex_df
        self._data_np = history_np
        self.dates = history_multiindex_df.index
        self.initial_capital = initial_capital
        self.num_features = history_np.shape[2]
        self.feature_index = feature_index
        self.reward_type = reward_type
        self.max_steps = steps

        assert reward_type in [
            "log_reward",
            "sharpe_ratio",
            "diferencial_sharpe_ratio",
        ], "Reward type not understood"

        self._normalized_np = (
            normalized_history_np if normalized_history_np is not None else history_np
        )
        self.start_date = start_date
        self.random_initialization = random_initialization

        self.src = DataGenerator(
            self._data_np,
            self.dates,
            abbreviation,
            normalized_np=self._normalized_np,
            steps=steps,
            window_length=window_length,
            include_cash=False,
            feature_index=feature_index,
        )

        self.sim = PortfolioSimulator(
            asset_names=abbreviation,
            trading_cost=trading_cost,
            steps=steps,
            p0=initial_capital,
        )

        num_assets = len(self.src.asset_names)
        self.previous_action = np.random.dirichlet(
            alpha=np.ones(num_assets + 1)
        ).astype(np.float32)

        self.action_space = gym.spaces.Box(
            0, 1, shape=(num_assets + 1,), dtype=np.float32
        )
        self.observation_space = spaces.Dict(
            {
                "price_tensor": gym.spaces.Box(
                    low=-np.inf,
                    high=np.inf,
                    shape=(window_length, num_assets, self.num_features),
                    dtype=np.float32,
                ),
                "weight": gym.spaces.Box(
                    low=0, high=1, shape=(num_assets,), dtype=np.float32
                ),
            }
        )

        self.historical_info_list = []

    def step(self, action) -> tuple[dict, float, bool, dict]:
        """Ejecuta un paso en el entorno usando la acción proporcionada.

        Args:
            action (np.ndarray): Vector de pesos del portafolio.

        Returns:

            obs (dict): Observaciones del entorno.
            reward (float): Recompensa del paso.
            done (bool): True si el episodio ha terminado.
            info (dict): Información adicional del paso.
        """
        return self._step(action)

    def _step(self, action) -> tuple[dict, float, bool, dict]:
        """Ejecuta un paso en el entorno usando la acción proporcionada."""
        action = np.exp(action) / (np.exp(action).sum() + eps)
        # action = sparsemax(action)

        observation, close1, open2, done1 = self.src._step()

        if len(action.shape) == 2:
            action = action[0]

        open2 = open2.reshape(-1)
        close1 = close1.reshape(-1)

        log_reward, info, done2 = self.sim._step(
            action, self.previous_action, close1, open2
        )
        self.previous_action = action

        info.update(
            {
                "date": self.dates[self.src.idx + self.src.step],
                "idx": self.src.idx,
                "step": self.src.step,
                "position": self.src.idx + self.src.step,
                "action": action,
                "next_simple_return": open2,
                "gto_norm": np.dot(open2, open2),
            }
        )

        self.historical_info_list.append(info)
        sharpe_ratio_log = sharpe_from_list(
            self.historical_info_list, "retorno_logaritmico"
        )
        if (
            np.isnan(sharpe_ratio_log)
            or np.isinf(sharpe_ratio_log)
            or abs(sharpe_ratio_log) > 1e4
        ):
            sharpe_ratio_log = 0
        info["sharpe_ratio"] = sharpe_ratio_log

        reward = log_reward if self.reward_type == "log_reward" else sharpe_ratio_log

        obs = {"price_tensor": observation, "weight": action[1:]}
        done = done1 or done2

        return obs, reward, done, False, info

    def reset(self, seed=None, options=None) -> tuple[dict, dict]:
        """Reinicia el entorno y devuelve la primera observación."""
        return self._reset(seed, options)

    def _reset(self, seed=None, options=None) -> tuple[dict, dict]:
        """Reinicia el entorno y devuelve la primera observación."""
        super().reset(seed=seed)
        self.historical_info_list = []
        self.sim.reset()

        start_date = (
            self.start_date
            if self.start_date and not self.random_initialization
            else None
        )
        observation = self.src.reset(start_date=start_date)
        self.start_idx = self.src.idx

        num_assets = len(self.src.asset_names)
        self.previous_action = np.random.dirichlet(
            alpha=np.ones(num_assets + 1)
        ).astype(np.float32)

        obs = {"price_tensor": observation, "weight": self.previous_action[1:]}
        return obs, {}

    def render(self, mode="human"):
        """Imprime el estado actual del entorno."""
        last_info = self.historical_info_list[-1] if self.historical_info_list else {}
        print(
            f"Step: {last_info.get('step', 0)} | Date: {last_info.get('date', 'N/A')} | Portfolio Value: {last_info.get('valor_portafolio', 0)} | Reward: {last_info.get('recompensa_acumulada', 0)} | Sharpe Ratio: {last_info.get('sharpe_ratio', 0)} | Cost: {last_info.get('coste', 0)}"
        )

    def close(self):
        pass

    def plot(self):
        """Genera gráficos de métricas del portafolio a lo largo del tiempo."""
        df_info = pd.DataFrame(self.historical_info_list)
        df_info["date"] = pd.to_datetime(df_info["date"], format="%Y-%m-%d")
        df_info.set_index("date", inplace=True)

        mdd_s = max_drawdown(df_info["retorno_simple"])
        sharpe_ratio_s = sharpe(df_info["retorno_simple"])

        mdd_log = max_drawdown(df_info["retorno_logaritmico"])
        sharpe_ratio_log = sharpe(df_info["retorno_logaritmico"])

        for column in [
            "valor_portafolio",
            "recompensa_acumulada",
            "retorno_simple",
            "retorno_logaritmico",
            "coste",
        ]:
            mean_value = df_info[column].mean()
            plt.figure()
            df_info[[column]].plot(title=column, fig=plt.gcf(), rot=30)
            plt.axhline(
                y=mean_value,
                color="r",
                linestyle="--",
                label=f"Mean {column}: {mean_value:.5f}",
            )
            plt.legend()
