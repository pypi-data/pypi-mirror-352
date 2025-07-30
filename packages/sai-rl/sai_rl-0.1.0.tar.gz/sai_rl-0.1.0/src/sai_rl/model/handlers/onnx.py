from typing import Any, Optional
from sai_rl.model.handlers._base import BaseModelHandler

from sai_rl.sai_console import SAIConsole

import numpy as np
import gymnasium as gym

IMPORT_ERROR_MESSAGE = (
    "ONNX Runtime is not installed. Please install it using 'pip install onnxruntime'."
)


class OnnxModelHandler(BaseModelHandler):
    _ort: Any = None
    _ort_available: bool = False

    def __init__(self, env: gym.Env, console: Optional[SAIConsole] = None):
        super().__init__(env, console)
        try:
            import onnxruntime as ort

            self._ort = ort
            self._ort_available = True
        except ImportError:
            self._ort_available = False
            raise ImportError(IMPORT_ERROR_MESSAGE)

    def _check_ort_available(self) -> None:
        if not self._ort_available:
            raise ImportError(IMPORT_ERROR_MESSAGE)

    def load_model(self, model_path: str):
        self._check_ort_available()
        return self._ort.InferenceSession(
            model_path, providers=["CPUExecutionProvider"]
        )

    def get_policy(self, model: Any, obs: np.ndarray):
        """
        Get the action from the model given an observation.
        Args:
            model (onnxruntime.InferenceSession): The ONNX model.
            obs (np.ndarray): The observation input to the model.
            is_continuous (bool): If True, the model is for continuous action space.
        Returns:
            int: The action selected by the model.
        Raises:
            ImportError: If PyTorch is not installed.
        """

        self._check_ort_available()

        if len(obs.shape) < self.obs_space_dims + 1:
            obs = np.expand_dims(obs, axis=0)

        return model.run(None, {"input": obs})[0]

    def save_model(self, model, model_path):
        self._check_ort_available()
        if self._console:
            self._console.warning(
                "Saving ONNX models is not supported. The model will not be saved."
            )
        pass

    def export_to_onnx(self, model, model_path):
        self._check_ort_available()
        if self._console:
            self._console.warning(
                "Exporting to ONNX is not supported. The model will not be exported."
            )
        pass
