import gymnasium as gym
from typing import Optional

from sai_rl.error import ModelError
from sai_rl.types import ModelLibraryType

from sai_rl.model.handlers._base import BaseModelHandler

from sai_rl.sai_console import SAIConsole


def get_handler(
    env: gym.Env, model_type: ModelLibraryType, console: Optional[SAIConsole]
) -> BaseModelHandler:
    if model_type == "pytorch":
        from sai_rl.model.handlers.pytorch import PyTorchModelHandler

        handler = PyTorchModelHandler(env, console)
    elif model_type == "tensorflow":
        from sai_rl.model.handlers.tensorflow import TensorFlowModelHandler

        handler = TensorFlowModelHandler(env, console)
    elif model_type == "keras":
        from sai_rl.model.handlers.keras import KerasModelHandler

        handler = KerasModelHandler(env, console)
    elif model_type == "stable_baselines3":
        from sai_rl.model.handlers.sb3 import SBL3ModelHandler

        handler = SBL3ModelHandler(env, console)
    elif model_type == "onnx":
        from sai_rl.model.handlers.onnx import OnnxModelHandler

        handler = OnnxModelHandler(env, console)
    else:
        raise ModelError(f"Unsupported model type: {model_type}")

    return handler


__all__ = ["get_handler", "BaseModelHandler"]
