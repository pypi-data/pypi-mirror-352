from datetime import datetime

import numpy as np
from stable_baselines3 import DDPG, PPO, SAC, TD3
from stable_baselines3.common.callbacks import CallbackList, CheckpointCallback
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.logger import configure
from stable_baselines3.common.noise import (
    NormalActionNoise,
    OrnsteinUhlenbeckActionNoise,
)
from stable_baselines3.common.vec_env import VecNormalize

from quant_drl.data.stock_data import StockData
from quant_drl.environment.portfolio_environment import PortfolioEnvironment
from quant_drl.networks.custom_networks import (
    CustomCNNFeatureExtractor,
    CustomCNNLSTMFeatureExtractor,
    CustomExtremeCNNLSTMFeatureExtractor,
    CustomLoggingCallback,
    CustomLSTMFeatureExtractor,
    CustomTransformerFeatureExtractor,
)

LOGS_DIR = "../logs/"
SAVE_DIR = "../models/"


class Trainer:
    def __init__(
        self,
        configuration,
        generate_default_name: bool = True,
        run: bool = False,
        logs_dir: str = LOGS_DIR,
        save_dir: str = SAVE_DIR,
    ):
        self.configuration = configuration

        # Calcular fechas de entrenamiento y evaluación
        end_eval_date = self.configuration["end_date"]
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

        # Obtener y normalizar datos
        stock_data = self.get_stock_data(
            self.configuration["companies"],
            self.configuration["features"],
            self.configuration["indicators"],
            start_train_date,
            start_eval_date,
        )

        norm_data = self.normalize_data(stock_data, self.configuration["normalize"])

        # Crear entorno vectorizado y normalizado
        raw_env = make_vec_env(
            lambda: self.make_env(stock_data, norm_data, self.configuration), n_envs=1
        )
        self.vec_env = VecNormalize(raw_env, norm_obs=False, norm_reward=True)

        # Seleccionar algoritmo
        self.model = self.select_algorithm(
            self.configuration["algorithm"],
            self.vec_env,
            self.configuration["learning_rate"],
            self.configuration["feature"],
            self.configuration["lstm_layers"],
        )

        self.generate_default_name = generate_default_name
        self.logs_dir = logs_dir
        self.save_dir = save_dir

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        if self.generate_default_name:
            feature_name = self.configuration["feature"] or "NoFeature"
            self.base_dir = f"{self.configuration['algorithm']}/{feature_name}/{self.configuration['algorithm']}_reward_{self.configuration['reward_type']}_normalize_{self.configuration['normalize']}_ncompanies_{len(self.configuration['companies'])}_{timestamp}_lr_{self.configuration['learning_rate']}"
        else:
            model_name = f"{self.configuration['model_name']}_{timestamp}"
            self.base_dir = f"USERS/{self.configuration['user_id']}/{model_name}"

        if run:
            self.run_experiment()

    def get_stock_data(self, companies, features, indicators, start_train, end_eval):
        """Crea una instancia de StockData con los parámetros indicados."""
        return StockData(
            comp_abv=[c["abv"] for c in companies],
            comp_names=[c["name"] for c in companies],
            features=features,
            end_date=end_eval,
            start_date=start_train,
            include_cash=False,
            technical_indicators=indicators,
        )

    def normalize_data(self, stock_data, method):
        """Normaliza los datos históricos usando el método especificado."""
        if method == "min_max":
            return stock_data.gross_return_data_normalized_min_max
        elif method == "power_transform":
            return stock_data.gross_return_data_power_transformed
        elif method == "standard":
            return stock_data.gross_return_data_normalized_standard
        return None

    def make_env(self, stock_data, norm_data, config):
        """Crea el entorno personalizado para entrenamiento."""
        return PortfolioEnvironment(
            history_np=stock_data.gross_return_data_numpy,
            history_multiindex_df=stock_data.multi_index_df,
            abbreviation=stock_data.comp_abv,
            normalized_history_np=norm_data,
            trading_cost=config["trading_cost"],
            window_length=config["window_length"],
            steps=config["steps"],
            reward_type=config["reward_type"],
            feature_index=config["feature_index"],
            initial_capital=config["initial_capital"],
        )

    def select_algorithm(
        self, algo_name, env, learning_rate, feature=None, lstm_layers=2
    ):
        """Devuelve una instancia del modelo basado en el algoritmo y extractor indicados."""
        num_assets = env.observation_space["weight"].shape[0]

        policy_kwargs = None
        if feature == "CNN":
            policy_kwargs = dict(
                features_extractor_class=CustomCNNFeatureExtractor,
                features_extractor_kwargs={
                    "num_assets": num_assets,
                    "features_dim": 32 * num_assets,
                },
            )
        elif feature == "LSTM":
            policy_kwargs = dict(
                features_extractor_class=CustomLSTMFeatureExtractor,
                features_extractor_kwargs={
                    "num_assets": num_assets,
                    "lstm_layers": lstm_layers,
                },
            )
        elif feature == "ExtremeCNNLSTM":
            policy_kwargs = dict(
                features_extractor_class=CustomExtremeCNNLSTMFeatureExtractor,
                features_extractor_kwargs={
                    "num_assets": num_assets,
                    "lstm_layers": lstm_layers,
                },
            )
        elif feature == "Transformer":
            policy_kwargs = dict(
                features_extractor_class=CustomTransformerFeatureExtractor,
                features_extractor_kwargs={},
            )
        elif feature == "CNNLSTM":
            policy_kwargs = dict(
                features_extractor_class=CustomCNNLSTMFeatureExtractor,
                features_extractor_kwargs={
                    "num_assets": num_assets,
                    "lstm_layers": lstm_layers,
                },
            )

        algo_params = {
            "policy": "MultiInputPolicy",
            "env": env,
            "verbose": 2,
            "learning_rate": learning_rate,
            "policy_kwargs": policy_kwargs,
        }

        if algo_name == "PPO":
            return PPO(
                **algo_params, batch_size=128, gamma=0.999, n_steps=100, ent_coef=0.01
            )
        elif algo_name == "DDPG":
            return DDPG(
                **algo_params,
                buffer_size=int(1e4),
                batch_size=128,
                action_noise=NormalActionNoise(
                    mean=np.zeros(env.action_space.shape),
                    sigma=0.1 * np.ones(env.action_space.shape),
                ),
            )
        elif algo_name == "TD3":
            return TD3(
                **algo_params,
                buffer_size=int(1e4),
                action_noise=OrnsteinUhlenbeckActionNoise(
                    mean=np.zeros(env.action_space.shape),
                    sigma=0.2 * np.ones(env.action_space.shape),
                    theta=0.15,
                ),
            )
        elif algo_name == "SAC":
            return SAC(
                **algo_params,
                buffer_size=int(1e4),
                batch_size=128,
                action_noise=NormalActionNoise(
                    mean=np.zeros(env.action_space.shape),
                    sigma=0.1 * np.ones(env.action_space.shape),
                ),
            )

        raise ValueError(f"Algorithm '{algo_name}' not recognized.")

    def run_experiment(self):
        """Corre un experimento completo: crea el entorno, entrena el modelo y guarda resultados."""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

        # Configurar paths de guardado
        self.log_dir = f"{self.logs_dir}/{self.base_dir}/"
        self.save_path = f"{self.save_dir}/{self.base_dir}/"
        name_prefix = "model"

        # Configurar logger y callbacks
        self.model.set_logger(configure(self.log_dir, ["csv", "tensorboard"]))
        checkpoint_callback = CheckpointCallback(
            save_freq=self.configuration["checkpoint_freq"],
            save_path=self.save_path,
            name_prefix=name_prefix,
        )
        callback_list = CallbackList([checkpoint_callback, CustomLoggingCallback()])

        # Entrenar modelo
        self.model.learn(
            total_timesteps=self.configuration["total_timesteps"],
            progress_bar=True,
            callback=callback_list,
        )
        self.model.save(f"{self.save_path}{name_prefix}_final")

        # Guardar hiperparámetros
        with open(f"{self.save_path}{name_prefix}_hyperparameters.txt", "w") as f:
            for key, value in self.configuration.items():
                f.write(f"{key.upper()}: {value}\n")

        self.vec_env.close()
