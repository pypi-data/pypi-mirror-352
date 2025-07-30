import os
import time
import numpy as np
import contextlib
from urllib.parse import urlsplit
from typing import List

from lumeo.utils import debug_log_if, error_log
from lumeo.utils import run_command, install_import

tritonclient = install_import('tritonclient[http]', version='2.33')
import tritonclient.utils.shared_memory as shm


class TritonRemoteModelUsingSHM:
  """
  Client for interacting with a remote Triton Inference Server model.
  Attributes:
      url (str): The URL of the Triton server.
      endpoint (str): The name of the model on the Triton server.
      scheme (str): The communication scheme ('http' or 'grpc').
      auto_manage (bool): Whether to automatically manage shared memory regions.
      input_max_dims (List[List(int)]): Maximum dimensions for input tensors.
      output_max_dims (List[List(int)]): Maximum dimensions for output tensors.
  """

  def __init__(self,
               url: str,
               endpoint: str = "",
               scheme: str = "",
               deployment_id: str = "",
               node_id: str = "",
               auto_manage: bool = True,
               input_max_dims=None,
               output_max_dims=None,
               enable_debug_logs=False,
               compare_outputs=False,
               unload_unused_model=True):
    """
    Initialize the TritonRemoteModelUsingSHM.
    Arguments may be provided individually or parsed from a collective 'url' argument of the form
        <scheme>://<netloc>/<endpoint>/<task_name>
    Args:
        url (str): The URL of the Triton server.
        endpoint (str): The name of the model on the Triton server.
        scheme (str): The communication scheme ('http' or 'grpc').
        deployment_id (str): The ID of the deployment.
        node_id (str): The ID of the node.
        auto_manage (bool): Whether to automatically manage shared memory regions.
        input_max_dims (List[List(int)], optional): Maximum dimensions for input tensors.
        output_max_dims (List[List(int)], optional): Maximum dimensions for output tensors.
        enable_debug_logs (bool): Whether to enable debug logs.
        compare_outputs (bool): Whether to compare outputs.
        unload_unused_model (bool): Whether to unload unused model.
    """
    if not endpoint and not scheme:  # Parse all args from URL string
      splits = urlsplit(url)
      endpoint = splits.path.strip("/").split("/")[0]
      scheme = splits.scheme
      url = splits.netloc

    self.model_name = self.endpoint = endpoint

    self.unique_key = f"{deployment_id}_{node_id}.{self.model_name}"
    self.url = url
    self.node_id = node_id
    self.auto_manage = auto_manage
    self.input_max_dims = input_max_dims
    self.output_max_dims = output_max_dims
    self.enable_debug_logs = enable_debug_logs
    self.compare_outputs = compare_outputs
    self.unload_unused_model = unload_unused_model

    # Choose the Triton client based on the communication scheme
    # Ref : https://github.com/triton-inference-server/client/blob/main/src/python/library/tritonclient/http/_client.py
    import tritonclient.http as client  # noqa
    self.triton_client = client.InferenceServerClient(url=url, verbose=False, ssl=False, concurrency=5)
    self.InferRequestedOutput = client.InferRequestedOutput
    self.InferInput = client.InferInput

    # Load model, and get config.
    self.is_model_loaded = False
    if self.auto_manage:
      self.load_model()

    self.is_shm_setup = False
    if self.auto_manage:
      self.setup_shared_memory()

    return

  def is_model_installed(self):
    """
    Check if the model is installed on the Triton server.

    Returns:
        bool: True if the model is installed, False otherwise.
    """
    triton_model_file = f"/var/lib/lumeo/models/triton_model_repo/{self.model_name}/1/{self.model_name}.onnx"
    return os.path.exists(triton_model_file)

  def clear_cache(self):
    """
    Clear the cache for the Triton model.
    """
    triton_cache_path = f"/var/lib/lumeo/models/triton_model_cache/{self.model_name}"
    triton_model_path = f"/var/lib/lumeo/models/triton_model_repo/{self.model_name}"
    run_command(f"rm -rf {triton_cache_path}", None, 'Clearing Triton cache', node_id=self.node_id)
    run_command(f"rm -rf {triton_model_path}", None, 'Clearing Triton model', node_id=self.node_id)

  def install_model(self, onnx_file, enable_trt=False):
    """
    Install the model on the Triton server.

    Args:
        onnx_file (str): The path to the ONNX file.
        enable_trt (bool): Whether to enable TensorRT optimization.
    """
    triton_model_file = f"/var/lib/lumeo/models/triton_model_repo/{self.model_name}/1/{self.model_name}.onnx"
    triton_model_config = f"/var/lib/lumeo/models/triton_model_repo/{self.model_name}/config.pbtxt"
    triton_cache_path = f"/var/lib/lumeo/models/triton_model_cache/{self.model_name}"

    # make directory
    os.makedirs(os.path.dirname(triton_model_file), exist_ok=True)
    os.makedirs(triton_cache_path, exist_ok=True)

    run_command(f"mv -f {onnx_file} {triton_model_file}", None, 'Moving ONNX file to triton model directory', node_id=self.node_id)

    # TRT execution provider for ONNX runtime will create TRT engine, and
    # cache it to the specified directory.
    # Ref : https://github.com/triton-inference-server/onnxruntime_backend
    model_config = (f"name: \"{self.model_name}\"\n"
                    "platform: \"onnxruntime_onnx\"\n"
                    "max_batch_size: 1\n"
                    f"default_model_filename: \"{triton_model_file.split('/')[-1]}\"\n"
                    "instance_group [\n"
                    "    {\n"
                    "        kind: KIND_GPU\n"
                    "        count: 1\n"
                    "        gpus: 0\n"
                    "    }\n"
                    "]\n")
    if enable_trt:
      model_config += ("optimization { execution_accelerators {\n"
                       "    gpu_execution_accelerator : [ {\n"
                       "        name : \"tensorrt\"\n"
                       "        parameters { key: \"precision_mode\" value: \"FP16\" }\n"
                       "        parameters { key: \"max_workspace_size_bytes\" value: \"1073741824\" }\n"
                       "        parameters { key: \"trt_engine_cache_enable\" value: \"true\" }\n"
                       f"       parameters {{ key: \"trt_engine_cache_path\" value: \"{triton_cache_path}\" }}\n"
                       "    }]\n"
                       "}}\n")

    with open(triton_model_config, 'w') as f:
      f.write(model_config)

    return self

  def get_model_state(self):
    """
    Get the state of the model on the Triton server.

    Returns:
        tuple: A tuple containing two boolean values:
            - is_loaded (bool): True if the model is loaded, False otherwise.
            - is_loading (bool): True if the model is loading, False otherwise.
    """
    with contextlib.suppress(Exception):
      triton_models = self.triton_client.get_model_repository_index()
      for model in triton_models:
        if model["name"] == self.model_name:
          if 'state' not in model:
            return False, False
          else:
            return model['state'] == 'READY', model['state'] == 'LOADING'
    return False, False

  def load_model(self):
    """
    Load the model on the Triton server.

    Raises:
        Exception: If there is an error loading the model.
    """
    is_loaded, is_loading = self.get_model_state()
    if not (is_loaded or is_loading):
      with contextlib.suppress(Exception):
        self.triton_client.load_model(self.model_name)
    while not self.triton_client.is_model_ready(self.model_name):
      debug_log_if(f"Waiting for Triton model {self.model_name} to be ready.", self.enable_debug_logs, self.node_id)
      time.sleep(10)

    is_loaded, is_loading = self.get_model_state()
    if is_loaded:
      config = self.triton_client.get_model_config(self.model_name)

      # Sort output names alphabetically, i.e. 'output0', 'output1', etc.
      config["output"] = sorted(config["output"], key=lambda x: x.get("name"))

      # Define model attributes
      type_map = {"TYPE_FP32": np.float32, "TYPE_FP16": np.float16, "TYPE_UINT8": np.uint8, "TYPE_INT64": np.int64}
      to_int = lambda x: [int(e) for e in x]

      self.input_formats = [x["data_type"] for x in config["input"]]
      self.input_dims = [to_int(x["dims"]) for x in config["input"]]
      self.np_input_formats = [type_map[x] for x in self.input_formats]
      self.input_names = [x["name"] for x in config["input"]]
      if self.input_max_dims:
        self.input_dims = [self.input_max_dims[input_name] for input_name in self.input_names]

      self.output_formats = [x["data_type"] for x in config["output"]]
      self.output_dims = [to_int(x["dims"]) for x in config["output"]]
      self.np_output_formats = [type_map[x] for x in self.output_formats]
      self.output_names = [x["name"] for x in config["output"]]
      if self.output_max_dims:
        self.output_dims = [self.output_max_dims[output_name] for output_name in self.output_names]

      if any(-1 in dim for dim in self.input_dims + self.output_dims):
        raise Exception("Model's Input or output dimensions contain -1. Please specify max dimensions in constructor.")

      # Compute total input and output byte size
      self.total_input_byte_size = int(
        sum([np.prod(dim) * np.dtype(format).itemsize for dim, format in zip(self.input_dims, self.np_input_formats)]))
      self.total_output_byte_size = int(sum(
        [np.prod(dim) * np.dtype(format).itemsize for dim, format in zip(self.output_dims, self.np_output_formats)]))

      self.is_model_loaded = True
    else:
      raise Exception(f"Error loading model {self.model_name}.")

    return self

  def unload_model_if_unused(self):
    """
    Unload the model from the Triton server if it is not being used by any deployment.

    Returns:
        bool: True if the model was unloaded, False otherwise.
    """
    is_loaded, is_loading = self.get_model_state()
    if is_loaded:
      with contextlib.suppress(Exception):
        deployments_using_model = set()
        triton_shms = self.triton_client.get_system_shared_memory_status()
        for triton_shm in triton_shms:
          if self.model_name in triton_shm['name']:
            deployments_using_model.add(triton_shm['name'].split('.')[1].split('_')[0])

        if len(deployments_using_model) == 0:
          debug_log_if(f"Unloading Triton model {self.model_name} as it is not being used by any deployment.", self.enable_debug_logs, self.node_id)
          self.triton_client.unload_model(self.model_name)
          return True

    return self

  def setup_shared_memory(self):
    """
    Setup shared memory regions for input and output data.
    """
    self.unregister_shared_memory(True)

    with contextlib.suppress(Exception):
      # Create and register shared memory regions for inputs and outputs
      self.shm_ip_handle = shm.create_shared_memory_region(
        f"input_data.{self.unique_key}", f"/input.{self.unique_key}", self.total_input_byte_size
      )
      self.shm_op_handle = shm.create_shared_memory_region(
        f"output_data.{self.unique_key}", f"/output.{self.unique_key}", self.total_output_byte_size
      )
      self.triton_client.register_system_shared_memory(
        f"input_data.{self.unique_key}", f"/input.{self.unique_key}", self.total_input_byte_size
      )
      self.triton_client.register_system_shared_memory(
        f"output_data.{self.unique_key}", f"/output.{self.unique_key}", self.total_output_byte_size
      )
      self.is_shm_setup = True
    return self

  def unregister_shared_memory(self, force=False):
    """
    Unregister shared memory regions with the Triton server.

    Args:
        force (bool): Whether to force unregistering shared memory regions.
    """
    if self.is_shm_setup or force:
      with contextlib.suppress(Exception):
        self.triton_client.unregister_system_shared_memory(f'input_data.{self.unique_key}')
      with contextlib.suppress(Exception):
        self.triton_client.unregister_system_shared_memory(f'output_data.{self.unique_key}')
      with contextlib.suppress(Exception):
        shm.destroy_shared_memory_region(self.shm_ip_handle)
      with contextlib.suppress(Exception):
        shm.destroy_shared_memory_region(self.shm_op_handle)
      self.is_shm_setup = False
      debug_log_if(f"Unregistered shared memory regions with Triton server.", self.enable_debug_logs, self.node_id)
    return self

  def __del__(self):
    """
    Destructor to ensure no shared memory regions are registered with the server.
    """
    if self.auto_manage or self.unload_unused_model:
      self.unregister_shared_memory()
      self.unload_model_if_unused()

  def __call__(self, *inputs: np.ndarray) -> List[np.ndarray]:
    """
    Call the model with the given inputs.

    Args:
        *inputs (List[np.ndarray]): Input data to the model.

    Returns:
        List[np.ndarray]: Model outputs.
    """
    if self.compare_outputs:
      output_shm = self.predict_shm(*inputs)
      output_noshm = self.predict_noshm(*inputs)
      assert self.compare_shm_noshm_outputs(output_shm[0], output_noshm[0])
      return output_shm
    else:
      if self.is_shm_setup:
        return self.predict_shm(*inputs)
      else:
        return self.predict_noshm(*inputs)

  def predict_noshm(self, *inputs: np.ndarray) -> dict:
    """
    Call the model with the given inputs without using shared memory.

    Args:
        *inputs (List[np.ndarray]): Input data to the model.

    Returns:
        dict: Model outputs keyed by output names.
    """
    infer_inputs = []
    for i, x in enumerate(inputs):
      if i == 0:
        input_format = x.dtype
      if x.dtype != self.np_input_formats[i]:
        x = x.astype(self.np_input_formats[i])
      infer_input = self.InferInput(self.input_names[i], [*x.shape], self.input_formats[i].replace("TYPE_", ""))
      infer_input.set_data_from_numpy(x)
      infer_inputs.append(infer_input)

    infer_outputs = [self.InferRequestedOutput(output_name) for output_name in self.output_names]
    outputs = self.triton_client.infer(model_name=self.model_name, inputs=infer_inputs, outputs=infer_outputs)

    # Read results from the outputs and create a dictionary
    output_data = {}
    for output_name in self.output_names:
      output_data[output_name] = outputs.as_numpy(output_name).astype(input_format)

    return output_data

  def predict_shm(self, *inputs: np.ndarray) -> dict:
    """
    Call the model with the given inputs using shared memory.

    Args:
        *inputs (List[np.ndarray]): Input data to the model.

    Returns:
        dict: Model outputs keyed by output names.
    """
    offset = 0
    infer_inputs = []
    for i, input in enumerate(inputs):
      if input.dtype != self.np_input_formats[i]:
        input = input.astype(self.np_input_formats[i])
      shm.set_shared_memory_region(self.shm_ip_handle, [input], offset=offset)
      infer_input = self.InferInput(self.input_names[i], [*input.shape], self.input_formats[i].replace("TYPE_", ""))
      infer_input.set_shared_memory(f"input_data.{self.unique_key}", input.size * input.itemsize, offset=offset)
      infer_inputs.append(infer_input)
      offset += input.size * input.itemsize

    offset = 0
    infer_outputs = []
    for i, output_name in enumerate(self.output_names):
      output_size = int(np.prod(self.output_dims[i]) * np.dtype(self.np_output_formats[i]).itemsize)
      infer_output = self.InferRequestedOutput(output_name, binary_data=True)
      infer_output.set_shared_memory(f"output_data.{self.unique_key}", output_size, offset=offset)
      infer_outputs.append(infer_output)
      offset += output_size

    # Perform inference
    results = self.triton_client.infer(model_name=self.model_name, inputs=infer_inputs, outputs=infer_outputs)

    # Read results from the shared memory
    output_data = {}
    offset = 0
    for i, output_name in enumerate(self.output_names):
      output = results.get_output(output_name)
      if output is not None:
        output_data_np = shm.get_contents_as_numpy(
          self.shm_op_handle,
          tritonclient.utils.triton_to_np_dtype(output["datatype"]),
          output["shape"],
          offset=offset,
        )
        output_data[output_name] = output_data_np
        offset += output_data_np.size * output_data_np.itemsize
      else:
        debug_log_if(f"{output_name} is missing in the response.", self.enable_debug_logs, self.node_id)

    return output_data

  def compare_shm_noshm_outputs(self, output_shm, output_noshm):
    """
    Compare the outputs of shared memory and non-shared memory predictions.

    Args:
        output_shm (np.ndarray): Output from shared memory prediction.
        output_noshm (np.ndarray): Output from non-shared memory prediction.

    Returns:
        bool: True if the outputs are equal, False otherwise.
    """
    debug_log_if(f"output_shm: {output_shm}", self.enable_debug_logs, self.node_id)
    debug_log_if(f"output_noshm: {output_noshm}", self.enable_debug_logs, self.node_id)

    debug_log_if(f"output_shm shape: {output_shm.shape}", self.enable_debug_logs, self.node_id)
    debug_log_if(f"output_shm numpy type: {output_shm.dtype}", self.enable_debug_logs, self.node_id)

    debug_log_if(f"output_noshm shape: {output_noshm.shape}", self.enable_debug_logs, self.node_id)
    debug_log_if(f"output_noshm numpy type: {output_noshm.dtype}", self.enable_debug_logs, self.node_id)

    if output_shm.shape != output_noshm.shape:
      return False

    return np.array_equal(output_shm, output_noshm)