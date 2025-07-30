from typing import Optional, Any

from sai_rl.model.handlers._base import BaseModelHandler
from sai_rl.sai_console import SAIConsole

import gymnasium as gym
import numpy as np

IMPORT_ERROR_MESSAGE = (
    "TensorFlow is not installed. Please install it using 'pip install sai_rl[tf]'."
)


class TensorFlowModelHandler(BaseModelHandler):
    _tf: Any = None
    _tf_v1: Any = None
    _tf2onnx: Any = None
    _onnx: Any = None
    _tf_available: bool = False

    def __init__(self, env: gym.Env, console: Optional[SAIConsole] = None):
        super().__init__(env, console)
        try:
            import tensorflow.compat.v1 as tf_v1
            import tensorflow as tf
            import tf2onnx
            import onnx

            self._tf = tf
            self._tf_v1 = tf_v1
            self._tf2onnx = tf2onnx
            self._onnx = onnx
            self._tf_available = True
        except ImportError:
            self._tf_available = False
            raise ImportError(IMPORT_ERROR_MESSAGE)

    def _check_tensorflow_available(self) -> None:
        if not self._tf_available:
            raise ImportError(IMPORT_ERROR_MESSAGE)

    def is_tf1_model(self, model) -> bool:
        return hasattr(model, "sess")

    def is_tf2_model(self, model) -> bool:
        return (callable(model) and hasattr(model, '__call__')) or isinstance(model, self._tf.Module)        

    def load_model(self, model_path: str):
        self._check_tensorflow_available()

        model = None
        tf2_load_successful = False
        try:
            model = self._tf.saved_model.load(model_path)
            tf2_load_successful = self.is_tf2_model(model)
        except Exception as e:
            print(f"TF2 model load failed: {str(e)}")

        if tf2_load_successful:
            return model
        elif model is not None:
            raise ValueError("Loaded TF2 model is not recognized as valid.")

        print("Falling back to TF1 model loader...")
        return self._load_model_v1(model_path)

    def _load_model_v1(self, model_path):
        self._check_tensorflow_available()

        import tensorflow.compat.v1 as tf
        tf.disable_eager_execution()        

        class FrozenTF1Model:
            def __init__(self, model_path: str, input_name: str = "states:0", output_name: str = "policy:0"):
                self.graph = tf.Graph()
                with tf.gfile.GFile(model_path, "rb") as f:
                    graph_def = tf.GraphDef()
                    graph_def.ParseFromString(f.read())

                with self.graph.as_default():
                    tf.import_graph_def(graph_def, name="")

                self.sess = tf.Session(graph=self.graph)
                self.states = self.graph.get_tensor_by_name(input_name)
                self.policy = self.graph.get_tensor_by_name(output_name)

            def select_action(self, state: np.ndarray):
                state = np.expand_dims(state, axis=0) if state.ndim == 1 else state
                return self.sess.run(self.policy, feed_dict={self.states: state})[0]

        return FrozenTF1Model(model_path, input_name="states:0", output_name="policy:0")

    def get_policy(self, model, obs: np.ndarray) -> np.ndarray:
        self._check_tensorflow_available()

        if len(obs.shape) < self.obs_space_dims + 1:
            obs = np.expand_dims(obs, axis=0)

        if self.is_tf1_model(model):
            return model.sess.run(model.policy, feed_dict={model.states: obs})
        elif self.is_tf2_model(model):
            return np.array(model(obs))
        elif hasattr(model, "predict"):
            return np.array(model.predict(obs, verbose=0))
        else:
            raise ValueError("Unknown model type: cannot compute policy.")

    def save_model(self, model, model_path):
        self._check_tensorflow_available()

        if self.is_tf1_model(model):
            from tensorflow.compat.v1.graph_util import convert_variables_to_constants

            sess = model.sess
            output_node_names = [model.policy.name.split(":")[0]]
            frozen_graph_def = convert_variables_to_constants(
                sess, sess.graph.as_graph_def(), output_node_names=output_node_names
            )
            self._tf_v1.io.write_graph(frozen_graph_def, logdir=".", name=model_path, as_text=False)
        elif self.is_tf2_model(model):
            self._tf.saved_model.save(model, model_path.replace(".pb", ""))

        return model_path

    def export_to_onnx_v1(self, model, model_path: str):
        from tensorflow.compat.v1.graph_util import convert_variables_to_constants

        sess = model.sess
        input_names = [model.states.name]
        output_names = [model.policy.name]

        # Freeze variables into constants
        frozen_graph_def = convert_variables_to_constants(
            sess,
            sess.graph_def,
            output_node_names=[name.split(":")[0] for name in output_names],
        )

        onnx_model, _ = self._tf2onnx.convert.from_graph_def(
            frozen_graph_def,
            input_names=input_names,
            output_names=output_names,
            opset=11,
        )

        self._onnx.save_model(
            onnx_model,
            model_path if model_path.endswith(".onnx") else f"{model_path}.onnx",
        )

    def export_to_onnx_v2(self, model, model_path: str):
        input_shape = [None, *self.observation_space.shape]
        input_spec = self._tf.TensorSpec(input_shape, self._tf.float32, name="input")

        # Wrap model in a tracing function
        @self._tf.function
        def wrapped_model(x):
            return model(x)

        # Manually create concrete function
        concrete_func = wrapped_model.get_concrete_function(input_spec)

        onnx_model, _ = self._tf2onnx.convert.from_function(
            wrapped_model,
            input_signature=[input_spec],
            opset=11
        )

        self._onnx.save_model(
            onnx_model,
            model_path if model_path.endswith(".onnx") else f"{model_path}.onnx",
        )

    def export_to_onnx(self, model, model_path: str):
        self._check_tensorflow_available()
        if self.is_tf1_model(model):
            self.export_to_onnx_v1(model, model_path)
        elif self.is_tf2_model(model):
            self.export_to_onnx_v2(model, model_path)            
