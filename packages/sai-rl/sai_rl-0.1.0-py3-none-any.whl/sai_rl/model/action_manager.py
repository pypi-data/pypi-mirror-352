import time
from typing import Optional, Callable

import os
import re
import inspect
import requests

import numpy as np
import gymnasium as gym

from rich.syntax import Syntax

from sai_rl.utils import config
from sai_rl.sai_console import SAIConsole, SAIStatus
from sai_rl.error import ActionFunctionError, NetworkError


class ActionFunctionManager:
    _console: Optional[SAIConsole]
    _env: Optional[gym.Env]

    def __init__(
        self,
        action_function: Optional[str | Callable] = None,
        download_dir: str = config.temp_path,
        env: Optional[gym.Env] = None,
        verbose: bool = False,
        console: Optional[SAIConsole] = None,
        status: Optional[SAIStatus] = None,
    ):
        self._console = console
        self._env = env

        self.verbose = verbose

        self._action_function = None
        self._action_function_source = None

        self._download_dir = download_dir
        self._path = None

        if status:
            status.update("Loading action function...")

        self.load(action_function, status)

    def _print(self):
        if not self._action_function_source:
            return

        if not self._console:
            return

        panel_group = self._console.group(
            Syntax(self._action_function_source, "python", theme="github-dark"),
        )

        panel = self._console.panel(
            panel_group, title="Action Function", padding=(1, 2)
        )

        self._console.print()
        self._console.print(panel)

    def _load_from_code(self, code: str, status: Optional[SAIStatus] = None):
        if status:
            status.update("Loading action function from code...")

        clean_code = self.remove_imports(code)

        function_name = None
        for line in clean_code.splitlines():
            if line.strip().startswith("def "):
                function_name = line.strip().split("def ")[1].split("(")[0].strip()
                break

        if not function_name:
            raise ActionFunctionError(
                "No function definition found in the provided code"
            )

        namespace = dict({"np": np, "env": self._env})
        exec(clean_code, namespace)

        self._action_function = namespace[function_name]
        self._action_function_source = clean_code

    def _load_from_file(self, path: str, status: Optional[SAIStatus] = None):
        if status:
            status.update("Loading action function from file...")

        self._path = path
        if not os.path.exists(path):
            raise ActionFunctionError(f"File not found: {path}")

        with open(path, "r") as f:
            code = f.read()
            self._load_from_code(code)

    def _load_from_url(self, url: str, status: Optional[SAIStatus] = None):
        if status:
            status.update("Downloading action function from URL...")
            status.stop()

        if not self._download_dir:
            raise ActionFunctionError("Download path not set")

        os.makedirs(self._download_dir, exist_ok=True)
        action_path = f"{self._download_dir}/{time.time()}.py"

        if os.path.exists(action_path):
            os.remove(action_path)

        try:
            if self._console:
                with self._console.progress("Downloading action function") as progress:
                    with requests.get(url, stream=True) as response:
                        response.raise_for_status()
                        total_size = int(response.headers.get("content-length", 0))
                        task = progress.add_task("Downloading...", total=total_size)

                        chunk_size = 8192  # 8 KB
                        downloaded_size = 0

                        with open(action_path, "wb") as f:
                            for chunk in response.iter_content(chunk_size=chunk_size):
                                if chunk:
                                    f.write(chunk)
                                    downloaded_size += len(chunk)
                                    progress.update(task, advance=len(chunk))
            else:
                with requests.get(url) as response:
                    response.raise_for_status()
                    with open(action_path, "wb") as f:
                        f.write(response.content)

        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Failed to download action function: {e}")

        if status:
            status.start()

        self._load_from_file(action_path, status)

    @staticmethod
    def remove_imports(code_string: str) -> str:
        """Remove import statements from code for security."""
        pattern = re.compile(
            r"^\s*#?\s*(from\s+\w+\s+import\s+.*|import\s+\w+.*|from\s+\w+\s+import\s+\(.*\)|import\s+\(.*\))",
            re.MULTILINE,
        )
        return re.sub(pattern, "", code_string)

    def get_action(self, obs: np.ndarray) -> np.ndarray:
        if self._action_function is None:
            raise ActionFunctionError("Action function not loaded")

        return self._action_function(obs)  # type: ignore

    def load(
        self,
        action_fn: Optional[str | Callable] = None,
        status: Optional[SAIStatus] = None,
    ):
        if status:
            status.update("Loading action function...")

        if not action_fn:
            if self._console:
                self._console.warning("No action function provided, skipping load.")
            return

        if isinstance(action_fn, str):
            if action_fn.startswith(("http://", "https://")):
                self._load_from_url(action_fn, status)
            elif action_fn.endswith((".py")) and os.path.exists(action_fn):
                self._load_from_file(action_fn, status)
            elif action_fn.startswith("def"):
                self._load_from_code(action_fn, status)
            else:
                raise ActionFunctionError(
                    f"Unsupported action function path: {action_fn}"
                )
        elif callable(action_fn):
            action_fn_source = inspect.getsource(action_fn)
            self._load_from_code(action_fn_source)
        else:
            raise ActionFunctionError(
                f"Unsupported action function type: {type(action_fn)}"
            )

        if self.verbose:
            self._print()

        if self._console:
            self._console.success("Successfully loaded action function.")

    def save_action_function(self, path: str):
        if not self._action_function_source:
            raise ActionFunctionError("No action function loaded")

        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path), exist_ok=True)

        if os.path.exists(path):
            raise ActionFunctionError(f"File already exists: {path}")

        if not path.endswith(".py"):
            raise ActionFunctionError("File must end with .py")

        with open(path, "w") as f:
            f.write(self._action_function_source)
        self._path = path

    def clean(self):
        if self._path and os.path.exists(self._path):
            os.remove(self._path)
            self._path = None
        self._action_function = None
        self._action_function_source = None
