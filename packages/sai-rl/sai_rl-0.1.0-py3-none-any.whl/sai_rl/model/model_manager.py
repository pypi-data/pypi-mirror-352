from typing import Optional, Callable

import os
import requests
import gymnasium as gym

from rich.align import Align
from rich.text import Text

from sai_rl.model.action_manager import ActionFunctionManager
from sai_rl.sai_console import SAIConsole, SAIStatus

from sai_rl.utils import config
from sai_rl.error import ModelError, NetworkError
from sai_rl.types import ModelType, ModelLibraryType

from sai_rl.model.handlers import get_handler, BaseModelHandler


class ModelManager:
    _console: Optional[SAIConsole]
    _env: gym.Env

    _model_type: ModelLibraryType
    _model: ModelType
    _handler: BaseModelHandler
    _action_manager: Optional[ActionFunctionManager] = None

    def __init__(
        self,
        env: gym.Env,
        model: ModelType,
        model_type: Optional[ModelLibraryType] = None,
        action_function: Optional[str | Callable] = None,
        download_dir: str = config.temp_path,
        console: Optional[SAIConsole] = None,
        status: Optional[SAIStatus] = None,
    ):
        if status is not None:
            status.update("Loading model...")

        self._console = console
        self._env = env

        self._download_dir = download_dir

        self._model_type = self._determine_model_type(model, model_type, status)
        self._model, self._handler = self._load_model(model, status)

        if action_function is not None:
            self._action_manager = ActionFunctionManager(
                action_function=action_function,
                download_dir=self._download_dir,
                env=self._env,
                verbose=True,
                console=self._console,
                status=status,
            )

        self._print(status=status)

        if self._console:
            self._console.success("Successfully loaded model.")

    def _determine_model_type(
        self,
        model: ModelType,
        model_type: Optional[ModelLibraryType],
        status: Optional[SAIStatus] = None,
    ) -> ModelLibraryType:
        determined_model_type = None

        if self._console:
            self._console.debug(f"Determining model type for {model}")

        if status is not None:
            status.update("Determining model type for model...")

        if isinstance(model, str):
            if model.startswith(("http://", "https://")):
                if model_type is None:
                    raise ModelError("model_type must be provided for URL models.")
                determined_model_type = model_type
            elif os.path.exists(model):
                determined_model_type = self._determine_file_type(model)
            else:
                raise ModelError(f"Invalid model path or URL: {model}")
        else:
            model_type_detected = False
            for cls in model.__class__.__mro__:
                cls_path = f"{cls.__module__}.{cls.__name__}"
                if cls_path.startswith("torch.nn.") or "torch" in cls.__module__:
                    determined_model_type = "pytorch"
                    model_type_detected = True
                    break
                elif "tensorflow" in cls.__module__:
                    determined_model_type = "tensorflow"
                    model_type_detected = True
                    break
                elif "keras" in cls.__module__:
                    determined_model_type = "keras"
                    model_type_detected = True
                    break
                elif "stable_baselines3" in cls.__module__:
                    determined_model_type = "stable_baselines3"
                    model_type_detected = True
                    break
                elif "onnx" in cls.__module__:
                    determined_model_type = "onnx"
                    model_type_detected = True
                    break

            # Fallback for raw TF1 models
            sess = getattr(model, "sess", None)
            if sess:
                sess_class = sess.__class__
                if (
                    hasattr(sess_class, "__module__")
                    and "tensorflow" in sess_class.__module__.lower()
                    and "session" in sess_class.__name__.lower()
                    and hasattr(model, "states")
                ):
                    return "tensorflow"

            if not model_type_detected:
                if model_type is not None:
                    determined_model_type = model_type
                else:
                    raise ModelError(
                        "Could not automatically determine model type. Please specify 'model_type' parameter explicitly."
                    )

        if determined_model_type is None:
            raise ModelError(
                "Could not determine model type. Please specify 'model_type' parameter explicitly."
            )

        if model_type and determined_model_type != model_type:
            raise ModelError(
                f"Provided model_type '{model_type}' does not match detected type '{determined_model_type}'"
            )

        if self._console:
            self._console.debug(f"Determined model type: {determined_model_type}")
        return determined_model_type

    def _determine_file_type(self, file_path: str) -> ModelLibraryType:
        _, ext = os.path.splitext(file_path)
        if ext in [".pt", ".pth"]:
            return "pytorch"
        elif ext in [".pb"]:
            return "tensorflow"
        elif ext in [".h5", ".keras"]:
            return "keras"
        elif ext == ".zip":
            return "stable_baselines3"
        elif ext == ".onnx":
            return "onnx"
        else:
            raise ModelError(f"Unsupported file type: {ext}")

    def _load_model(self, model: ModelType, status: Optional[SAIStatus] = None):
        if self._console:
            self._console.debug(f"Loading model: {model}")

        loaded_model = None
        loaded_handler = None

        if isinstance(model, str) and model.startswith(("http://", "https://")):
            model_path = self._download_model(model, status)
            if status is not None:
                status.update("Loading model...")
                status.stop()
            loaded_handler = get_handler(self._env, self._model_type, self._console)
            loaded_model = loaded_handler.load_model(model_path)

        elif self._model_type in ["pytorch", "tensorflow", "keras", "stable_baselines3", "onnx"]:
            loaded_handler = get_handler(self._env, self._model_type, self._console)
            if isinstance(model, str):
                if status is not None:
                    status.update("Loading model...")
                    status.stop()
                loaded_model = loaded_handler.load_model(model)
            else:
                loaded_model = model
        else:
            raise ModelError(f"Unsupported model type: {self._model_type}")

        if status is not None:
            status.start()

        if self._console:
            self._console.debug(
                f"Loaded model: {loaded_model} with handler: {loaded_handler}"
            )
        return loaded_model, loaded_handler

    def _download_model(self, model_url: str, status: Optional[SAIStatus] = None):
        if self._console:
            self._console.debug(f"Downloading model from {model_url}")

        if status is not None:
            status.update("Downloading model...")
            status.stop()

        os.makedirs(self._download_dir, exist_ok=True)
        filename = model_url.split("/")[-1].split("?")[0]
        file_extension = {
            "stable_baselines3": ".zip",
            "pytorch": ".pt",
            "keras": ".keras",
            "tensorflow": ".pb",
            "onnx": ".onnx",
        }.get(self._model_type, "")
        model_path = os.path.join(self._download_dir, filename + file_extension)

        try:
            if self._console:
                with self._console.progress("Downloading model") as progress:
                    with requests.get(model_url, stream=True) as response:
                        response.raise_for_status()
                        total_size = int(response.headers.get("content-length", 0))
                        task = progress.add_task(
                            "[green]Downloading...", total=total_size
                        )

                        chunk_size = 8192  # 8 KB
                        downloaded_size = 0

                        with open(model_path, "wb") as f:
                            for chunk in response.iter_content(chunk_size=chunk_size):
                                if chunk:
                                    f.write(chunk)
                                    downloaded_size += len(chunk)
                                    progress.update(task, advance=len(chunk))
            else:
                with requests.get(model_url) as response:
                    response.raise_for_status()
                    with open(model_path, "wb") as f:
                        f.write(response.content)

        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Failed to download model: {e}")

        if status is not None:
            status.start()

        return model_path

    def _print(self, status: Optional[SAIStatus] = None):
        if status:
            status.update("Processing model...")

        if not self._console:
            return

        title = "Model"
        env_id = (
            self._env.spec.id
            if hasattr(self._env, "spec") and self._env.spec is not None
            else "Unknown"
        )
        info_group = f"""[bold cyan]Type:[/bold cyan]          {self._model_type}
[bold cyan]Environment:[/bold cyan]    {env_id}
[bold cyan]Action Function:[/bold cyan]  {"Custom" if self._action_manager else f"Default ({'sample' if self._handler.is_continuous else 'argmax'})"}"""

        panel_group = self._console.group(
            Align.left(Text.from_markup(info_group)),
        )

        panel = self._console.panel(panel_group, title=title, padding=(1, 2))
        self._console.print()
        self._console.print(panel)

    def get_action(self, obs):
        if self._action_manager:
            policy = self._handler.get_policy(self._model, obs)
            return self._action_manager.get_action(policy)

        return self._handler.get_action(self._model, obs)

    def save_model(self, model_path, use_onnx=False, **kwargs):
        if os.path.exists(model_path):
            raise ModelError(f"Model path already exists: {model_path}")

        os.makedirs(os.path.dirname(model_path), exist_ok=True)

        if use_onnx:
            self._handler.export_to_onnx(self._model, model_path)
        else:
            self._handler.save_model(self._model, model_path)

    def save_action_function(self, action_fn_path: str):
        if self._action_manager:
            self._action_manager.save_action_function(action_fn_path)
        else:
            raise ModelError("No action function loaded.")

    @property
    def model_type(self):
        return self._model_type

    @property
    def model(self):
        return self._model
