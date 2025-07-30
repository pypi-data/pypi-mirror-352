from typing import Any, TYPE_CHECKING, Optional
from sai_rl.model.handlers._base import BaseModelHandler

from sai_rl.sai_console import SAIConsole

import numpy as np
import gymnasium as gym

if TYPE_CHECKING:
    import torch
    import torch.nn as nn

    PyTorchModel = nn.Module
    PyTorchTensor = torch.Tensor
else:
    PyTorchModel = Any
    PyTorchTensor = Any

IMPORT_ERROR_MESSAGE = (
    "PyTorch is not installed. Please install it using 'pip install sai_rl[torch]'."
)


class PyTorchModelHandler(BaseModelHandler):
    _torch: Any = None
    _torch_available: bool = False

    def __init__(self, env: gym.Env, console: Optional[SAIConsole] = None):
        super().__init__(env, console)
        try:
            import torch

            self._torch = torch
            self._torch_available = True
        except ImportError:
            self._torch_available = False
            raise ImportError(IMPORT_ERROR_MESSAGE)

    def _check_torch_available(self) -> None:
        if not self._torch_available:
            raise ImportError(IMPORT_ERROR_MESSAGE)

    def load_model(self, model_path: str, use_torchscript: bool = True) -> PyTorchModel:
        """
        Load a PyTorch model from the specified path.
        Args:
            model_path (str): Path to the model file.
            use_torchscript (bool): If True, load a TorchScript model. Otherwise, load a regular PyTorch model.
        Returns:
            torch.nn.Module: The loaded PyTorch model.
        Raises:
            ImportError: If PyTorch is not installed.
        """
        self._check_torch_available()

        if use_torchscript:
            model = self._torch.jit.load(model_path)
        else:
            model = self._torch.load(model_path)

        model.eval()
        return model

    def get_policy(self, model: PyTorchModel, obs: np.ndarray) -> np.ndarray:
        """
        Get the action from the model given an observation.
        Args:
            model (torch.nn.Module): The PyTorch model.
            obs (np.ndarray): The observation input to the model.
            is_continuous (bool): If True, the model is for continuous action space.
        Returns:
            int: The action selected by the model.
        Raises:
            ImportError: If PyTorch is not installed.
        """
        self._check_torch_available()

        if len(obs.shape) < self.obs_space_dims + 1:
            obs = np.expand_dims(obs, axis=0)

        obs_tensor = self._torch.from_numpy(obs)
        return model(obs_tensor).detach().numpy()

    def save_model(
        self, model: PyTorchModel, model_path: str, use_torchscript: bool = True
    ):
        """
        Save a PyTorch model to the specified path.
        Args:
            model (torch.nn.Module): The PyTorch model to save.
            model_path (str): Path to save the model file.
            use_torchscript (bool): If True, save as a TorchScript model. Otherwise, save as a regular PyTorch model.
        Returns:
            str: The path to the saved model file.
        Raises:
            ImportError: If PyTorch is not installed.
        """
        self._check_torch_available()

        if use_torchscript:
            if not isinstance(model, self._torch.jit.ScriptModule):
                obs_tensor = self._torch.from_numpy(
                    np.zeros(
                        (1, *self.observation_space.shape),
                        dtype=self.observation_space.dtype,
                    )
                )

                model = self._torch.jit.trace(
                    model,
                    self._torch.randn(
                        *obs_tensor.shape,
                        dtype=obs_tensor.dtype,
                    ),
                )
            self._torch.jit.save(model, model_path)
        else:
            self._torch.save(model, model_path)
        return model_path

    def export_to_onnx(self, model: PyTorchModel, model_path: str):
        self._check_torch_available()
        model.eval()

        torch_input = self._torch.from_numpy(
            np.zeros(
                (1, *self.observation_space.shape),
                dtype=self.observation_space.dtype,
            )
        )

        return self._torch.onnx.export(
            model,
            (torch_input,),
            model_path,
            export_params=True,
            opset_version=18,
            input_names=["input"],
            output_names=["output"],
            dynamic_axes={"input": {0: "batch_size"}, "output": {0: "batch_size"}},
        )
