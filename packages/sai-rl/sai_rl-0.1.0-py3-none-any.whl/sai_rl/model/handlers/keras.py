from typing import Optional, Any

from sai_rl.model.handlers._base import BaseModelHandler
from sai_rl.sai_console import SAIConsole

import gymnasium as gym
import numpy as np

IMPORT_ERROR_MESSAGE = (
    "TensorFlow is not installed. Please install it using 'pip install sai_rl[tf]'."
)


class KerasModelHandler(BaseModelHandler):
    _tf: Any = None
    _keras: Any = None
    _tf2onnx: Any = None
    _onnx: Any = None
    _tf_available: bool = False

    def __init__(self, env: gym.Env, console: Optional[SAIConsole] = None):
        super().__init__(env, console)
        try:
            import tensorflow as tf
            import keras
            import tf2onnx
            import onnx

            self._tf = tf
            self._keras = keras
            self._tf2onnx = tf2onnx
            self._onnx = onnx
            self._tf_available = True
            pass
        except ImportError:
            self._tf_available = False
            raise ImportError(IMPORT_ERROR_MESSAGE)

    def _check_tensorflow_available(self) -> None:
        if not self._tf_available:
            raise ImportError(IMPORT_ERROR_MESSAGE)

    def load_model(self, model_path):
        self._check_tensorflow_available()
        return self._keras.models.load_model(model_path)

    def get_policy(self, model, obs: np.ndarray) -> np.ndarray:
        self._check_tensorflow_available()

        if len(obs.shape) < self.obs_space_dims + 1:
            obs = np.expand_dims(obs, axis=0)

        state = self._tf.convert_to_tensor(obs, dtype=self.observation_space.dtype)
        policy = model(state)
        return np.array(policy)

    def save_model(self, model, model_path):
        self._check_tensorflow_available()
        model.save(model_path)

    def export_to_onnx(self, model, model_path: str):
        self._check_tensorflow_available()

        model.output_names = ["output"]
        input_signature = [
            self._tf.TensorSpec(
                [None, *self.observation_space.sample().shape],
                self._tf.float32,
                name="input",
            )
        ]
        onnx_model, _ = self._tf2onnx.convert.from_keras(
            model, input_signature=input_signature, opset=18
        )
        self._onnx.save(
            onnx_model,
            model_path if model_path.endswith(".onnx") else f"{model_path}.onnx",
        )
