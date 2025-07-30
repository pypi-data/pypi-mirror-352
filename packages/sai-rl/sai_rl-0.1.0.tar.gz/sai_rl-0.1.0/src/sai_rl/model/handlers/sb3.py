from typing import Any, TYPE_CHECKING, Optional
from sai_rl.model.handlers._base import BaseModelHandler

from sai_rl.sai_console import SAIConsole

import gymnasium as gym
import numpy as np

if TYPE_CHECKING:
    from stable_baselines3.common.policies import BasePolicy

    SB3BasePolicy = BasePolicy
else:
    SB3BasePolicy = Any

IMPORT_ERROR_MESSAGE = (
    "Stable Baselines3 is not installed. Please install it using 'pip install stable-baselines3'."
    " If you are using a custom model, please ensure it is compatible with Stable Baselines3."
)

class SBL3ModelHandler(BaseModelHandler):
    _torch: Any = None
    _sb3: Any = None
    _sb3_available: bool = False

    def __init__(self, env: gym.Env, console: Optional[SAIConsole] = None, algo="PPO"):
        super().__init__(env, console)

        try:
            import stable_baselines3 as sb3
            import torch

            self._sb3 = sb3
            self._torch = torch
            self._sb3_available = True
        except ImportError:
            self._sb3_available = False
            raise ImportError(IMPORT_ERROR_MESSAGE)

        self._algo = getattr(sb3, algo)

        class SB3TorchPolicy(torch.nn.Module):
            def __init__(self, policy: SB3BasePolicy):
                super().__init__()
                self.policy = policy

            def forward(self, observation: torch.Tensor):
                return self.policy(observation, deterministic=True)

        self._policy_class = SB3TorchPolicy

    def _check_sb3_available(self) -> None:
        if not self._sb3_available:
            raise ImportError(
                "Stable Baselines3 is not installed. Please install it using 'pip install stable-baselines3'."
            )

    def load_model(self, model_path) -> SB3BasePolicy:
        return self._algo.load(model_path)

    def get_policy(self, model: SB3BasePolicy, obs: Any) -> Any:
        if len(obs.shape) < self.obs_space_dims + 1:
            obs = np.expand_dims(obs, axis=0)

        return model.predict(obs, deterministic=True)[0]

    def get_action(self, model, obs: np.ndarray) -> np.ndarray:
        return self.get_policy(model, obs)

    def save_model(self, model, model_path):
        self._check_sb3_available()

        model.save(model_path)
        return model_path

    def export_to_onnx(self, model: SB3BasePolicy, model_path: str):
        self._check_sb3_available()

        torch_model = self._policy_class(model.policy)
        torch_model.eval()

        torch_input = self._torch.randn(
            1, *self.observation_space.shape, dtype=self.observation_space.dtype # type: ignore
        )

        return self._torch.onnx.export(
            torch_model,
            (torch_input,),
            model_path,
            export_params=True,
            opset_version=18,
            input_names=["input"],
            output_names=["output"],
            dynamic_axes={"input": {0: "batch_size"}, "output": {0: "batch_size"}},
        )
