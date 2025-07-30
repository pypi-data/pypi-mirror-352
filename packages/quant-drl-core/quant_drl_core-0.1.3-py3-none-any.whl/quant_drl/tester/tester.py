from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from stable_baselines3 import DDPG, PPO, SAC, TD3
from stable_baselines3.common.env_util import make_vec_env

from quant_drl.data.stock_data import StockData
from quant_drl.environment.portfolio_environment import PortfolioEnvironment
from quant_drl.networks.custom_networks import (
    CustomCNNLSTMFeatureExtractor,
    CustomLSTMFeatureExtractor,
)


def max_drawdown(pvs):
    peak = pvs[0]
    max_dd = 0
    for val in pvs:
        if val > peak:
            peak = val
        drawdown = (peak - val) / peak
        if drawdown > max_dd:
            max_dd = drawdown
    return max_dd


class Tester:
    """
    Clase encargada de evaluar modelos de Aprendizaje por Refuerzo para la gestión de portafolios.
    Maneja la carga de datos, normalización, entornos de entrenamiento y evaluación, y comparación de resultados.
    """

    def __init__(self, configuration, setup=True):
        """Inicializa el Tester con la configuración dada."""
        self.configuration = configuration
        if setup:
            self.setup_data()
            self.setup_envs()

    def setup_data(
        self, start_eval_date=None, end_eval_date=None, start_train_date=None
    ):
        """Carga los datos de mercado para entrenamiento y evaluación."""
        if start_eval_date is None:
            end_eval_date = self.configuration["end_eval_date"]
            start_eval_date = datetime(
                end_eval_date.year - self.configuration["length_eval_data"],
                end_eval_date.month,
                end_eval_date.day,
            )
            start_train_date = datetime(
                start_eval_date.year - self.configuration["length_train_data"],
                start_eval_date.month,
                start_eval_date.day,
            )

        companies = self.configuration["companies"]
        self.selected_abv = [c["abv"] for c in companies]
        self.selected_names = [c["name"] for c in companies]

        self.training_stock_data = StockData(
            comp_abv=self.selected_abv,
            comp_names=self.selected_names,
            features=self.configuration["features"],
            end_date=start_eval_date,
            start_date=start_train_date,
            include_cash=False,
            technical_indicators=self.configuration["indicators"],
        )

        self.eval_stock_data = StockData(
            comp_abv=self.selected_abv,
            comp_names=self.selected_names,
            features=self.configuration["features"],
            end_date=end_eval_date,
            start_date=start_eval_date,
            include_cash=False,
            technical_indicators=self.configuration["indicators"],
        )

        self.normalize_data()

    def normalize_data(self):
        """Aplica normalización a los datos de entrenamiento y evaluación según la configuración."""
        norm = self.configuration["normalize"]
        if norm == "min_max":
            attr = "gross_return_data_normalized_min_max"
        elif norm == "standard":
            attr = "gross_return_data_normalized_standard"
        else:
            attr = None

        if attr:
            self.training_normalized_history_np = getattr(
                self.training_stock_data, attr
            )
            self.eval_normalized_history_np = getattr(self.eval_stock_data, attr)
        else:
            self.training_normalized_history_np = None
            self.eval_normalized_history_np = None

    def setup_envs(
        self, start_train_date=None, start_eval_date=None, random_initialization=True
    ):
        """Inicializa entornos de entrenamiento y evaluación para el portafolio."""

        def make_env(stock_data, normalized_np, start_date=None):
            return PortfolioEnvironment(
                history_np=stock_data.gross_return_data_numpy,
                history_multiindex_df=stock_data.multi_index_df,
                abbreviation=stock_data.comp_abv,
                normalized_history_np=normalized_np,
                trading_cost=self.configuration["trading_cost"],
                window_length=self.configuration["window_length"],
                steps=self.configuration["steps"],
                reward_type=self.configuration["reward_type"],
                feature_index=self.configuration["feature_index"],
                initial_capital=self.configuration["initial_capital"],
                start_date=start_date,
                random_initialization=random_initialization,
            )

        self.port_train_env = make_vec_env(
            lambda: make_env(
                self.training_stock_data,
                self.training_normalized_history_np,
                start_train_date,
            ),
            n_envs=1,
        )
        self.port_eval_env = make_vec_env(
            lambda: make_env(
                self.eval_stock_data, self.eval_normalized_history_np, start_eval_date
            ),
            n_envs=1,
        )

    def reset_data_env(
        self, start_eval_date=None, end_eval_date=None, random_initialization=True
    ):
        """Resetea los datos y entornos de evaluación."""
        start_train_date = datetime(
            start_eval_date.year - self.configuration["length_train_data"],
            start_eval_date.month,
            start_eval_date.day,
        )

        self.setup_data(start_eval_date, end_eval_date, start_train_date)
        self.setup_envs(
            start_train_date=start_train_date,
            start_eval_date=start_eval_date,
            random_initialization=random_initialization,
        )

    def load_model(
        self,
        base_path: str,
        name: str = None,
        is_full_path: bool = False,
        steps: int = None,
        feature_extractor: str = None,
        algorithm: str = None,
        num_assets: int = 6,
        num_lstm_layers: int = 4,
    ):
        """Carga un modelo de entrenamiento desde disco."""
        if is_full_path:
            model_file = base_path
        else:
            model_file = (
                f"{base_path}/{name}/model_{steps}_steps"
                if steps
                else f"{base_path}/{name}/model_final"
            )

        if feature_extractor is None:
            if "CNNLSTM" in base_path:
                feature_extractor = "CNNLSTM"
            elif "LSTM" in base_path:
                feature_extractor = "LSTM"
            else:
                feature_extractor = None

        if algorithm is None:
            if "SAC" in base_path:
                algorithm = "SAC"
            elif "PPO" in base_path:
                algorithm = "PPO"
            elif "DDPG" in base_path:
                algorithm = "DDPG"
            elif "TD3" in base_path:
                algorithm = "TD3"
            else:
                algorithm = None

        policy_kwargs = None
        if feature_extractor == "CNNLSTM":
            policy_kwargs = dict(
                features_extractor_class=CustomCNNLSTMFeatureExtractor,
                features_extractor_kwargs={
                    "num_assets": num_assets,
                    "lstm_layers": num_lstm_layers,
                },
            )
        elif feature_extractor == "LSTM":
            policy_kwargs = dict(
                features_extractor_class=CustomLSTMFeatureExtractor,
                features_extractor_kwargs={
                    "num_assets": num_assets,
                    "lstm_layers": num_lstm_layers,
                },
            )
        else:
            custom_objects = None

        algo_params = {
            "policy": "MultiInputPolicy",
            "env": self.port_train_env,
            "verbose": 2,
            "policy_kwargs": policy_kwargs,
        }

        if algorithm == "SAC":
            self.model = SAC(**algo_params)
        elif algorithm == "DDPG":
            self.model = DDPG(**algo_params)
        elif algorithm == "TD3":
            self.model = TD3(**algo_params)
        elif algorithm == "PPO":
            self.model = PPO(**algo_params)

        self.model.set_parameters(model_file)

    def evaluate(
        self,
        env="eval",
        num_episodes=100,
        show_results=False,
        base_path=None,
        name=None,
        steps=None,
    ):
        """Evalúa el modelo entrenado en un entorno determinado."""
        if base_path and name:
            self.load_model(base_path, name, steps)

        env = self.port_eval_env if env == "eval" else self.port_train_env

        final_rewards, final_pvs = [], []
        mean_rewards, mean_sharpes, mean_pvs = [], [], []
        std_rewards, std_sharpes, std_pvs = [], [], []

        (
            all_rewards,
            all_sharpes,
            all_pvs,
            all_actions,
            all_episode_rewards,
            all_drawdowns,
        ) = ([], [], [], [], [], [])

        for _ in range(num_episodes):
            rewards, sharpes, actions, pvs, episode_rewards = (
                [],
                [],
                [],
                [],
                [],
            )
            obs = env.reset()
            done, episode_reward = False, 0.0
            while not done:
                action, _ = self.model.predict(obs, deterministic=True)
                softmax_action = np.exp(action) / np.sum(np.exp(action))
                obs, reward, done, info = env.step(action)

                rewards.append(float(reward))
                episode_reward += float(reward)
                sharpes.append(info[0]["sharpe_ratio"])
                pvs.append(info[0]["valor_portafolio"])
                actions.append(softmax_action)
                episode_rewards.append(episode_reward)

            final_rewards.append(episode_reward)
            final_pvs.append(pvs[-1])
            mean_rewards.append(float(np.mean(rewards)))
            mean_sharpes.append(float(np.mean(sharpes)))
            mean_pvs.append(float(np.mean(pvs)))
            std_rewards.append(float(np.std(rewards)))
            std_sharpes.append(float(np.std(sharpes)))
            std_pvs.append(float(np.std(pvs)))

            dd = max_drawdown(pvs)
            all_drawdowns.append(dd)

            all_rewards.append(rewards)
            all_sharpes.append(sharpes)
            all_pvs.append(pvs)
            all_actions.append(actions)
            all_episode_rewards.append(episode_rewards)

            if show_results:
                # Plot rewards
                fig = go.Figure()
                fig.add_trace(
                    go.Scatter(
                        x=np.arange(len(rewards)),
                        y=rewards,
                        mode="lines",
                        name="Rewards",
                    )
                )
                fig.update_layout(
                    title="Rewards", xaxis_title="Steps", yaxis_title="Reward"
                )
                fig.show()

                # Plot sharpes
                fig = go.Figure()
                fig.add_trace(
                    go.Scatter(
                        x=np.arange(len(sharpes)),
                        y=sharpes,
                        mode="lines",
                        name="Sharpes",
                    )
                )
                fig.update_layout(
                    title="Sharpes", xaxis_title="Steps", yaxis_title="Sharpe Ratio"
                )
                fig.show()

                # Plot pvs
                fig = go.Figure()
                fig.add_trace(
                    go.Scatter(
                        x=np.arange(len(pvs)),
                        y=pvs,
                        mode="lines",
                        name="Portfolio Value",
                    )
                )
                fig.update_layout(
                    title="Portfolio Value",
                    xaxis_title="Steps",
                    yaxis_title="Portfolio Value",
                )
                fig.show()

                # Plot actions with matplotlib
                selected_companies_abv = self.selected_abv
                selected_companies_names = self.selected_names
                actions_array = np.array(actions)
                # Crear la figura con Matplotlib and
                fig, ax = plt.subplots(figsize=(12, 6))

                colors = plt.cm.tab20.colors

                # Dibujar el área apilada con fondo oscuo
                actions_array = actions_array.reshape(
                    -1, len(selected_companies_abv) + 1
                )
                x = np.arange(actions_array.shape[0])
                ax.stackplot(
                    x,
                    actions_array.T,
                    labels=["Cash"] + selected_companies_names,
                    alpha=0.8,
                    colors=colors,
                )

                # Añadir leyenda
                ax.legend(loc="upper left")
                ax.set_title("Actions")
                ax.set_xlabel("Steps")
                ax.set_ylabel("Actions")

                plt.show()

        return {
            "final_rewards": final_rewards,
            "final_pvs": final_pvs,
            "final_drawdowns": all_drawdowns,
            "mean_rewards": mean_rewards,
            "mean_sharpes": mean_sharpes,
            "mean_pvs": mean_pvs,
            "std_rewards": std_rewards,
            "std_sharpes": std_sharpes,
            "std_pvs": std_pvs,
            "all_rewards": all_rewards,
            "all_sharpes": all_sharpes,
            "all_pvs": all_pvs,
            "all_actions": all_actions,
            "all_episode_rewards": all_episode_rewards,
        }

    def compare_train_eval(self, num_episodes=100, show_results=False):
        """Compara el desempeño del modelo en entrenamiento vs evaluación."""

        train_info = self.evaluate("train", num_episodes)
        eval_info = self.evaluate("eval", num_episodes)
        if show_results:
            self.plot_results(
                train_info["final_rewards"], eval_info["final_rewards"], "Final Rewards"
            )
            self.plot_results(
                train_info["mean_rewards"], eval_info["mean_rewards"], "Mean Rewards"
            )
            self.plot_results(
                train_info["mean_sharpes"],
                eval_info["mean_sharpes"],
                "Mean Sharpe Ratios",
            )
            self.plot_results(
                train_info["mean_pvs"], eval_info["mean_pvs"], "Mean Portfolio Values"
            )

        return train_info, eval_info

    @staticmethod
    def plot_results(train_values, eval_values, title):
        """Gráfica comparativa entre entrenamiento y evaluación."""
        plt.plot(train_values, label="Train")
        plt.plot(eval_values, label="Eval")
        plt.title(title)
        plt.grid()
        plt.legend()
        plt.show()
