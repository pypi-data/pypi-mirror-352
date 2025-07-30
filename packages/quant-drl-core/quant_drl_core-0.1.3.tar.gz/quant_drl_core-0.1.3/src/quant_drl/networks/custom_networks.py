import gym
import torch as th
import torch.nn as nn
import torch.nn.functional as F
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor


class CustomLoggingCallback(BaseCallback):
    def __init__(self, verbose=0):
        super().__init__(verbose)

    def _on_step(self):
        if "sharpe_ratio" in self.locals["infos"][0]:  # Acceder a `info`
            sr_metric_value = self.locals["infos"][0]["sharpe_ratio"]
            self.logger.record("rollout/sharpe_ratio", sr_metric_value)
        if "valor_portafolio" in self.locals["infos"][0]:
            pv_metric_value = self.locals["infos"][0]["valor_portafolio"]
            self.logger.record("rollout/valor_portafolio", pv_metric_value)
        if "recompensa_acumulada" in self.locals["infos"][0]:
            ar_metric_value = self.locals["infos"][0]["recompensa_acumulada"]
            self.logger.record("rollout/recompensa_acumulada", ar_metric_value)
        return True


class CustomCNNFeatureExtractor(BaseFeaturesExtractor):
    def __init__(self, observation_space, num_assets, features_dim=256):
        super(CustomCNNFeatureExtractor, self).__init__(observation_space, features_dim)
        self.conv1 = nn.Conv2d(
            in_channels=observation_space.get("price_tensor").shape[2],
            out_channels=32,
            kernel_size=(3, 1),
            padding="valid",
        )
        self.conv2 = nn.Conv2d(
            in_channels=32, out_channels=64, kernel_size=(3, 1), padding="valid"
        )
        self.conv3 = nn.Conv2d(
            in_channels=64,
            out_channels=32,
            kernel_size=(observation_space["price_tensor"].shape[0] - 4, 1),
            padding="valid",
        )

        self.bn1 = nn.BatchNorm2d(32)
        self.bn2 = nn.BatchNorm2d(64)
        self.bn3 = nn.BatchNorm2d(32)

        self.fc_weight = nn.Linear(num_assets, num_assets)

        self.conv1d_common = nn.Conv1d(in_channels=33, out_channels=32, kernel_size=1)
        self.bn_common = nn.BatchNorm1d(32)

        # **Salida final (128 * num_assets)**
        self._features_dim = 32 * num_assets  #

    def forward(self, observations):
        """Extrae características de las observaciones (dict -> tensor válido para SB3)"""
        price_tensor = observations[
            "price_tensor"
        ]  # (batch, window_length, num_assets, num_features)
        weight = observations["weight"]  # (batch, num_assets)

        # **1. Procesar price_tensor**
        price_tensor = price_tensor.permute(
            0, 3, 1, 2
        )  # (batch, num_features, window_length, num_assets)
        x = self.bn1(F.leaky_relu(self.conv1(price_tensor)))
        x = self.bn2(F.leaky_relu(self.conv2(x)))
        x = self.bn3(F.leaky_relu(self.conv3(x)))

        # **Aplanar eje de tiempo**
        x = x.squeeze(2)  # (batch, num_filters[2], num_assets)

        # **2. Procesar weight**
        w = self.fc_weight(weight)  # (batch, 16)
        w = w.unsqueeze(1)  # (batch, 1, 16)

        # **3. Fusionar price_tensor y weight**
        x = th.cat([x, w], dim=1)  # (batch, num_filters[2] + 1, num_assets)

        # **4. Aplicar Conv1D**
        x = self.bn_common(F.leaky_relu(self.conv1d_common(x)))

        # **5. Aplanar salida antes de la política y el valor**
        x_flat = x.view(x.shape[0], -1)  # (batch, 64 * num_assets)

        return x_flat


class CustomLSTMFeatureExtractor(BaseFeaturesExtractor):
    def __init__(self, observation_space, num_assets, features_dim=256, lstm_layers=4):
        super(CustomLSTMFeatureExtractor, self).__init__(
            observation_space, features_dim
        )

        # Input channels for LSTM (price_tensor is (batch, window_length, num_assets, num_features))
        input_size = (
            observation_space["price_tensor"].shape[2]
            * observation_space["price_tensor"].shape[1]
        )  # num_features

        # LSTM for price_tensor (seq_len = window_length, input_size = num_features)
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=num_assets,
            num_layers=lstm_layers,
            batch_first=True,
            dropout=0.2,
        )

        # Fully connected layer for processing weight information
        self.fc_weight = nn.Linear(num_assets, num_assets)

        # Final fully connected layer to combine both LSTM output and weight processed output
        self.conv1d_common = nn.Conv1d(in_channels=33, out_channels=32, kernel_size=1)
        self.bn_common = nn.BatchNorm1d(32)

        # Output feature dimension
        self._features_dim = 32 * num_assets  # The output size of the final dense layer

    def forward(self, observations):
        """Extract features from the observations (dict -> tensor valid for SB3)"""
        price_tensor = observations[
            "price_tensor"
        ]  # (batch, window_length, num_assets, num_features)
        weight = observations["weight"]  # (batch, num_assets)

        # Process price_tensor: (batch, window_length, num_assets, num_features)
        # Reshape price_tensor for LSTM: (batch, window_length, num_features * num_assets)

        price_tensor = price_tensor.view(
            price_tensor.shape[0], price_tensor.shape[1], -1
        )
        # Pass price_tensor through LSTM
        lstm_out, _ = self.lstm(price_tensor)  # (batch, window_length, hidden_dim)

        # Use the output from the last time step
        lstm_out = lstm_out[:, :32, :]  # (batch, hidden_dim)

        # Process weight information
        weight_processed = self.fc_weight(weight)  # (batch, 12)
        weight_processed = weight_processed.unsqueeze(1)  # (batch, 1, 12)

        # Concatenate LSTM output and weight features
        combined = th.cat([lstm_out, weight_processed], dim=1)

        # Final fully connected layer to combine both features
        combined = self.bn_common(F.leaky_relu(self.conv1d_common(combined)))

        combined_flat = combined.view(combined.shape[0], -1)

        return combined_flat


class CustomCNNLSTMFeatureExtractor(BaseFeaturesExtractor):
    def __init__(self, observation_space, num_assets, features_dim=512, lstm_layers=4):
        super(CustomCNNLSTMFeatureExtractor, self).__init__(
            observation_space, features_dim
        )

        self.conv1 = nn.Conv2d(
            in_channels=observation_space.get("price_tensor").shape[2],
            out_channels=32,
            kernel_size=(3, 1),
            padding="valid",
        )
        self.conv2 = nn.Conv2d(
            in_channels=32, out_channels=64, kernel_size=(3, 1), padding="valid"
        )
        self.conv3 = nn.Conv2d(
            in_channels=64,
            out_channels=32,
            kernel_size=(3, 1),
            padding="valid",
        )

        self.bn1 = nn.BatchNorm2d(32)
        self.bn2 = nn.BatchNorm2d(64)
        self.bn3 = nn.BatchNorm2d(32)

        lstm_input_size = observation_space["price_tensor"].shape[1] * 32

        self.lstm = nn.LSTM(
            input_size=lstm_input_size,
            hidden_size=num_assets,
            num_layers=lstm_layers,
            batch_first=True,
            dropout=0.2,
        )
        self.fc_weight = nn.Linear(num_assets, num_assets)

        self.conv1d_common = nn.Conv1d(in_channels=33, out_channels=32, kernel_size=1)
        self.bn_common = nn.BatchNorm1d(32)

        self._features_dim = 32 * num_assets

    def forward(self, observations):
        price_tensor = observations["price_tensor"]
        weight = observations["weight"]

        price_tensor = price_tensor.permute(0, 3, 1, 2)
        x = self.bn1(F.leaky_relu(self.conv1(price_tensor)))
        x = self.bn2(F.leaky_relu(self.conv2(x)))
        x = self.bn3(F.leaky_relu(self.conv3(x)))

        # expected output shape: (batch, num_filters[2], historical_window-6, num_assets)
        # expected lstm input shape (batch, historical_window-6, num_assets * num_filters[2])
        x = x.permute(0, 2, 1, 3)
        x = x.reshape(x.shape[0], x.shape[1], x.shape[2] * x.shape[3])

        lstm_out, _ = self.lstm(x)

        lstm_out = lstm_out[:, :32, :]
        weight_processed = self.fc_weight(weight)
        weight_processed = weight_processed.unsqueeze(1)

        combined = th.cat([lstm_out, weight_processed], dim=1)
        combined = self.bn_common(F.leaky_relu(self.conv1d_common(combined)))

        combined_flat = combined.view(combined.shape[0], -1)

        return combined_flat


class CustomExtremeCNNLSTMFeatureExtractor(BaseFeaturesExtractor):
    def __init__(self, observation_space, num_assets, features_dim=512, lstm_layers=4):
        super(CustomExtremeCNNLSTMFeatureExtractor, self).__init__(
            observation_space, features_dim
        )

        in_channels = observation_space["price_tensor"].shape[2]
        height = observation_space["price_tensor"].shape[0]
        width = observation_space["price_tensor"].shape[1]

        ### --- U-NET ENCODER --- ###
        self.enc_conv1 = nn.Sequential(
            nn.Conv2d(in_channels, 64, kernel_size=3, padding=1),
            nn.LeakyReLU(),
            nn.Conv2d(64, 64, kernel_size=3, padding=1),
            nn.LeakyReLU(),
        )

        self.pool1 = nn.MaxPool2d(kernel_size=2)

        self.enc_conv2 = nn.Sequential(
            nn.Conv2d(64, 32, kernel_size=3, padding=1),
            nn.GELU(),
            nn.Conv2d(32, 32, kernel_size=3, padding=1),
            nn.GELU(),
        )

        self.pool2 = nn.MaxPool2d(kernel_size=2)

        ### --- DECODER --- ###
        self.upconv1 = nn.ConvTranspose2d(32, 32, kernel_size=2, stride=2)
        self.dec_conv1 = nn.Sequential(
            nn.Conv2d(64, 64, kernel_size=3, padding=1),
            nn.LeakyReLU(),
            nn.Conv2d(64, 64, kernel_size=3, padding=1),
            nn.LeakyReLU(),
        )

        self.upconv2 = nn.ConvTranspose2d(64, in_channels, kernel_size=2, stride=2)
        self.dec_conv2 = nn.Sequential(
            nn.Conv2d(in_channels + in_channels, in_channels, kernel_size=3, padding=1),
            nn.LeakyReLU(),
            nn.Conv2d(in_channels, in_channels, kernel_size=3, padding=1),
            nn.LeakyReLU(),
        )

        ### --- LSTM --- ###
        lstm_input_size = width * in_channels
        self.lstm = nn.LSTM(
            input_size=lstm_input_size,
            hidden_size=num_assets,
            num_layers=lstm_layers,
            batch_first=True,
            dropout=0.2,
        )

        self.fc_weight = nn.Linear(num_assets, num_assets)

        ### --- Final conv1d for RL heads --- ###
        self.conv1d_common = nn.Conv1d(in_channels=33, out_channels=32, kernel_size=1)
        self.bn_common = nn.BatchNorm1d(32)

        self._features_dim = 32 * num_assets

    def center_crop(self, tensor, target_tensor):
        _, _, h, w = target_tensor.shape
        return tensor[:, :, :h, :w]

    def forward(self, observations):
        price_tensor = observations["price_tensor"]  # (B, H, W, C)
        weight = observations["weight"]

        x = price_tensor.permute(0, 3, 1, 2)  # (B, C, H, W)

        ### --- Encoder --- ###
        x1 = self.enc_conv1(x)  # (B, 64, H, W)
        x2 = self.pool1(x1)  # (B, 64, H/2, W/2)

        x3 = self.enc_conv2(x2)  # (B, 32, H/2, W/2)
        x4 = self.pool2(x3)  # (B, 32, H/4, W/4)

        ### --- Decoder --- ###
        u1 = self.upconv1(x4)  # (B, 32, H/2, W/2)
        x3_cropped = self.center_crop(x3, u1)
        c1 = th.cat([u1, x3_cropped], dim=1)

        d1 = self.dec_conv1(c1)  # (B, 64, H/2, W/2)
        u2 = self.upconv2(d1)  # (B, C, H, W)
        x_cropped = self.center_crop(x, u2)
        c2 = th.cat([u2, x_cropped], dim=1)  # Skip connection with original input
        d2 = self.dec_conv2(c2)  # (B, C, H, W)

        ### --- LSTM --- ###
        d2 = d2.permute(0, 2, 1, 3)  # (B, H, C, W)
        d2 = d2.reshape(d2.shape[0], d2.shape[1], -1)  # (B, H, C*W)

        lstm_out, _ = self.lstm(d2)  # (B, H, num_assets)
        lstm_out = lstm_out[:, :32, :]

        weight_processed = self.fc_weight(weight).unsqueeze(1)  # (B, 1, num_assets)
        combined = th.cat([lstm_out, weight_processed], dim=1)  # (B, 33, num_assets)

        combined = self.bn_common(F.leaky_relu(self.conv1d_common(combined)))
        combined_flat = combined.view(combined.shape[0], -1)

        return combined_flat


class CustomAdvancedLSTMFeatureExtractor(BaseFeaturesExtractor):
    def __init__(self, observation_space, num_assets, features_dim=512, lstm_layers=4):
        super(CustomAdvancedLSTMFeatureExtractor, self).__init__(
            observation_space, features_dim
        )

        input_size = (
            observation_space["price_tensor"].shape[2]
            * observation_space["price_tensor"].shape[1]
        )

        # Bidirectional LSTM for richer feature extraction
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=num_assets * 2,
            num_layers=lstm_layers,
            batch_first=True,
            bidirectional=True,
            dropout=0.3,
        )

        # Attention mechanism
        self.attention = nn.Linear(num_assets * 4, 1)

        self.extractor = nn.Conv2d(in_channels=1, out_channels=32, kernel_size=(2, 1))

        # Convolutional layers for temporal feature extraction
        self.conv1 = nn.Conv1d(
            in_channels=33, out_channels=32, kernel_size=3, padding=1
        )
        self.bn1 = nn.BatchNorm1d(32)

        self.conv2 = nn.Conv1d(
            in_channels=32, out_channels=16, kernel_size=3, padding=1
        )
        self.bn2 = nn.BatchNorm1d(16)

        # Fully connected layers for weight processing
        self.fc_weight1 = nn.Linear(num_assets, num_assets * 2)
        self.fc_weight2 = nn.Linear(num_assets * 2, num_assets * 4)

        # Final dense layers for feature integration
        self.fc_final1 = nn.Linear(64 * num_assets, 256)
        self.fc_final2 = nn.Linear(256, features_dim)

        self._features_dim = features_dim

    def forward(self, observations):
        price_tensor = observations[
            "price_tensor"
        ]  # (batch, window_length, num_assets, num_features)
        weight = observations["weight"]  # (batch, num_assets)

        price_tensor = price_tensor.view(
            price_tensor.shape[0], price_tensor.shape[1], -1
        )
        lstm_out, _ = self.lstm(price_tensor)

        # Attention mechanism
        weight_processed = F.relu(self.fc_weight1(weight))
        weight_processed = F.relu(self.fc_weight2(weight_processed))
        weight_processed = weight_processed.unsqueeze(1)  # (batch, 1, num_assets)

        attn_weights = F.softmax(self.attention(lstm_out), dim=1)  # (batch, seq_len, 1)
        attended_lstm = lstm_out * attn_weights
        expanded_lstm = attended_lstm.unsqueeze(1)
        extracted_features = self.extractor(expanded_lstm)
        assets_features = th.sum(extracted_features, dim=2)
        # lstm_out = th.sum(lstm_out * attn_weights, dim=1)  # (batch, hidden_dim)

        # Process weight information
        # Concatenate features
        combined = th.cat(
            [assets_features, weight_processed], dim=1
        )  # (batch, 1 + num_assets, hidden_dim)

        # Apply convolutions
        combined = self.bn1(F.relu(self.conv1(combined)))
        combined = self.bn2(F.relu(self.conv2(combined)))
        combined_flat = combined.view(combined.shape[0], -1)

        # Fully connected layers
        combined_flat = F.relu(self.fc_final1(combined_flat))
        combined_flat = self.fc_final2(combined_flat)

        return combined_flat


class CustomTransformerFeatureExtractor(BaseFeaturesExtractor):
    def __init__(
        self,
        observation_space: gym.spaces.Dict,
        features_dim: int = 256,
        d_model=64,
        nhead=4,
        num_layers=2,
    ):
        super().__init__(observation_space, features_dim)

        # Extract dimensions
        price_shape = observation_space[
            "price_tensor"
        ].shape  # (batch, historic_window, num_assets, num_features)
        historic_window, num_assets, num_features = price_shape

        # Linear projection to d_model (embedding dimension for Transformer)
        self.price_embedding = nn.Linear(num_features, d_model)

        # Transformer Encoder
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=num_assets * d_model,
            nhead=nhead,
            dim_feedforward=4 * num_assets * d_model,
        )
        self.transformer_encoder = nn.TransformerEncoder(
            encoder_layer, num_layers=num_layers
        )

        # Fully connected layer to reduce transformer output
        self.transformer_fc = nn.Linear(
            d_model * num_assets, 128
        )  # num_assets * d_model → 128-dim

        # MLP for previous_weights
        self.mlp_weights = nn.Sequential(nn.Linear(num_assets, 64), nn.ReLU())

        # Final fully connected layer
        self.fc_final = nn.Sequential(nn.Linear(128 + 64, features_dim), nn.ReLU())

    def forward(self, observations):
        # Process price tensor
        price_tensor = observations[
            "price_tensor"
        ]  # Shape: (batch, historic_window, num_assets, num_features)

        # Apply embedding layer
        embedded_prices = self.price_embedding(
            price_tensor
        )  # Shape: (batch, historic_window, num_assets, d_model)
        batch_size, historic_window, num_assets, d_model = embedded_prices.shape

        # Reshape and permute for transformer input: (seq_len, batch, embedding_dim)
        transformer_input = embedded_prices.permute(1, 0, 2, 3).reshape(
            historic_window, batch_size, num_assets * d_model
        )  # (historic_window, batch, num_assets * d_model)

        # Pass through transformer
        transformer_output = self.transformer_encoder(
            transformer_input
        )  # (historic_window, batch, num_assets * d_model)

        # Take the last time step's output
        last_output = transformer_output[-1]  # (batch, num_assets * d_model)

        # Reduce dimensionality
        price_features = self.transformer_fc(last_output)  # (batch, 128)

        # Process previous weights
        weights_features = self.mlp_weights(observations["weight"])  # (batch, 64)

        # Combine both feature sets
        combined_features = th.cat(
            [price_features, weights_features], dim=1
        )  # (batch, 128+64)

        return self.fc_final(combined_features)


class CustomActorCritic(nn.Module):
    def __init__(self, features_dim, num_assets):
        super(CustomActorCritic, self).__init__()

        # **Red de política (acciones)**
        self.policy_net = nn.Sequential(
            nn.Linear(features_dim, 128),
            nn.LeakyReLU(),
            nn.Linear(128, num_assets + 1),
        )

        # **Red de valor (estado-valor)**
        self.value_net = nn.Sequential(
            nn.Linear(features_dim, 128), nn.LeakyReLU(), nn.Linear(128, 1)
        )

    def forward(self, x):
        action_mean = self.policy_net(x)
        value = self.value_net(x)
        return action_mean, value


class CustomFeatureNetwork(nn.Module):
    def __init__(self, observation_space, num_assets):
        super(CustomFeatureNetwork, self).__init__()

        # Parámetros de la arquitectura
        num_filters = [32, 64, 128]  # Puedes cambiar esto
        kernel_size = (3, 1)  # Se aplica sobre el tiempo (temporal)
        activation = nn.LeakyReLU()

        # Capas convolucionales para price_tensor
        self.conv1 = nn.Conv2d(
            in_channels=observation_space["price_tensor"].shape[-1],
            out_channels=num_filters[0],
            kernel_size=kernel_size,
            padding="valid",
        )
        self.bn1 = nn.BatchNorm2d(num_filters[0])

        self.conv2 = nn.Conv2d(
            in_channels=num_filters[0],
            out_channels=num_filters[1],
            kernel_size=kernel_size,
            padding="valid",
        )
        self.bn2 = nn.BatchNorm2d(num_filters[1])

        self.conv3 = nn.Conv2d(
            in_channels=num_filters[1],
            out_channels=num_filters[2],
            kernel_size=(observation_space["price_tensor"].shape[0] - 4, 1),
            padding="valid",
        )
        self.bn3 = nn.BatchNorm2d(num_filters[2])

        # Procesar pesos de la cartera
        self.flatten = nn.Flatten()
        self.fc_weight = nn.Linear(num_assets, num_assets)

        # Capa Conv1D para feature fusion
        self.conv1d_common = nn.Conv1d(
            in_channels=num_filters[2] + 1, out_channels=64, kernel_size=1
        )
        self.bn_common = nn.BatchNorm1d(64)

        # Redes finales
        self.policy_net = nn.Sequential(
            nn.Linear(64 * num_assets, 128),
            activation,
            nn.Linear(128, num_assets + 1),  # Acción para cada activo + cash
        )

        self.value_net = nn.Sequential(
            nn.Linear(64 * num_assets, 128),
            activation,
            nn.Linear(128, 1),  # Escalar único como valor
        )

    def forward(self, observations):
        """Transforma las observaciones del diccionario en un tensor válido para SB3"""

        # Asegurar que las observaciones son un diccionario
        assert isinstance(observations, dict), (
            f"Expected dict but got {type(observations)}"
        )

        # Extraer entradas del diccionario
        price_tensor = observations[
            "price_tensor"
        ]  # (batch, window_length, num_assets, num_features)
        weight = observations["weight"]  # (batch, num_assets)

        # **1. Procesar price_tensor** (reordenar para Conv2D)
        price_tensor = price_tensor.permute(
            0, 3, 1, 2
        )  # (batch, num_features, window_length, num_assets)

        # Aplicar convoluciones
        x = self.bn1(F.leaky_relu(self.conv1(price_tensor)))
        x = self.bn2(F.leaky_relu(self.conv2(x)))
        x = self.bn3(F.leaky_relu(self.conv3(x)))

        # Aplanar eje de tiempo -> (batch, num_filters[2], num_assets)
        x = x.squeeze(2)

        # **2. Procesar weight** (mapear a 16 dimensiones)
        w = self.fc_weight(weight)  # (batch, 16)
        w = w.unsqueeze(1)  # (batch, 1, 16)

        # **3. Fusionar price_tensor y weight**
        x = th.cat([x, w], dim=1)  # (batch, num_filters[2] + 1, num_assets)

        # Aplicar Conv1D
        x = self.bn_common(F.leaky_relu(self.conv1d_common(x)))

        # **4. Aplanar salida antes de la política y el valor**

        x_flat = self.flatten(x)  # (batch, 64 * num_assets)

        # **5. Obtener acción y valor**
        action_mean = self.policy_net(x_flat)  # (batch, num_assets+1)
        value = self.value_net(x_flat)  # (batch, 1)

        return action_mean, value
