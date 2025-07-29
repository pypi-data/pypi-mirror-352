# Copyright 2020-2025 The HuggingFace Team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import json
import logging
import os
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any, AsyncGenerator, Iterator, Optional
import uuid
from fastapi.responses import JSONResponse, Response, StreamingResponse
import torch 
from transformers import AutoTokenizer
from deepreasoningwithtools.utils import CLIParser
from deepreasoningwithtools.import_utils import (
    is_fastapi_available,
    is_pydantic_available,
    is_uvicorn_available,
    is_vllm_ascend_available,
    is_vllm_available,
)
from deepreasoningwithtools.records import StreamingResponseTokenT

if is_fastapi_available():
    from fastapi import BackgroundTasks, FastAPI


if is_pydantic_available():
    from pydantic import BaseModel


if is_uvicorn_available():
    import uvicorn


# if is_vllm_available():
from vllm import LLM, SamplingParams
from vllm.distributed.device_communicators.pynccl import PyNcclCommunicator
from vllm.distributed.parallel_state import get_world_group
from vllm.distributed.utils import StatelessProcessGroup
from vllm.sampling_params import GuidedDecodingParams

if is_vllm_ascend_available():
    from vllm_ascend.distributed.device_communicators.pyhccl import PyHcclCommunicator as PyNcclCommunicator


logger = logging.getLogger(__name__)

# We use CUDA with multiprocessing, so we must use the 'spawn' start method. Otherwise, we will get the following
# error: RuntimeError: Cannot re-initialize CUDA in forked subprocess. To use CUDA with multiprocessing, you must use
# the 'spawn' start method
os.environ["VLLM_WORKER_MULTIPROC_METHOD"] = "spawn"


class WeightSyncWorkerExtension:
    """
    A vLLM worker extension that enables weight synchronization between a client and multiple server workers.

    This worker uses a `StatelessProcessGroup` to establish communication and a `PyNcclCommunicator` to handle
    efficient GPU-based communication using NCCL. The primary purpose of this class is to receive updated model weights
    from a client process and distribute them to all worker processes participating in model inference.
    """

    # The following attributes are initialized when `init_communicator` method is called.
    pynccl_comm = None  # Communicator for weight updates
    client_rank = None  # Source rank for broadcasting updated weights

    def init_communicator(self, host: str, port: int, world_size: int) -> None:
        """
        Initializes the weight update communicator using a stateless process group.

        This method creates a `StatelessProcessGroup` that allows external training processes to
        communicate with vLLM workers without interfering with the global torch distributed group.

        Args:
            host (`str`):
                Hostname or IP address of the master node.
            port (`int`):
                Port number to be used for communication.
            world_size (`int`):
                Total number of participating processes in the update group.
        """
        print("Checking if communicator is already initialized")
        if self.pynccl_comm is not None:
            raise RuntimeError("Weight update group already initialized. Call close_communicator first.")
        print("getting world group")
        # Get the rank of the current worker in the global world group.
        rank = get_world_group().rank

        # Create a stateless process group to manage communication between training processes and vLLM workers.
        print("creating stateless process group")
        pg = StatelessProcessGroup.create(host=host, port=port, rank=rank, world_size=world_size)

        # Initialize the NCCL-based communicator for weight synchronization.
        print("3"*20 + "Initializing communicator" + "3"*20)
        print("world_size", world_size)
        self.pynccl_comm = PyNcclCommunicator(pg, device=self.device)

        # The client process that sends updated weights has the highest rank (world_size - 1).
        self.client_rank = world_size - 1

    def update_named_param(self, name: str, dtype: torch.dtype, shape: Sequence[int]) -> None:
        """
        Receives updated weights from the client process and updates the named parameter in the model.

        Args:
            name (`str`):
                Name of the weight tensor being updated.
            dtype (`torch.dtype`):
                Data type of the weight tensor (e.g., `torch.float32`).
            shape (`Sequence[int]`):
                Shape of the weight tensor.
        """
        if self.pynccl_comm is None:
            raise RuntimeError("Communicator not initialized. Call `init_communicator` first.")

        # Allocate memory for the incoming weight tensor on the correct device.
        weight = torch.empty(shape, dtype=dtype, device=self.device)

        # Use NCCL to broadcast the updated weights from the client (src) to all workers.
        self.pynccl_comm.broadcast(weight, src=self.client_rank)
        self.pynccl_comm.group.barrier()

        # Load the received weights into the model.
        print("loading weights", name, weight.shape)
        self.model_runner.model.load_weights(weights=[(name, weight)])

    def close_communicator(self) -> None:
        """
        Closes the communicator when weight synchronization is no longer needed.

        This method deletes the NCCL communicator to release associated resources.
        """

        if self.pynccl_comm is not None:
            del self.pynccl_comm
            self.pynccl_comm = None  # Ensure attribute is reset to None
            self.client_rank = None  # Ensure attribute is reset to None


@dataclass
class ScriptArguments:
    r"""
    Arguments for the script.

    Args:
        model (`str`):
            Model name or path to load the model from.
        revision (`str` or `None`, *optional*, defaults to `None`):
            Revision to use for the model. If not specified, the default branch will be used.
        tensor_parallel_size (`int`, *optional*, defaults to `1`):
            Number of tensor parallel workers to use.
        host (`str`, *optional*, defaults to `"0.0.0.0"`):
            Host address to run the server on.
        port (`int`, *optional*, defaults to `8000`):
            Port to run the server on.
        gpu_memory_utilization (`float`, *optional*, defaults to `0.9`):
            Ratio (between 0 and 1) of GPU memory to reserve for the model weights, activations, and KV cache on the
            device dedicated to generation powered by vLLM. Higher values will increase the KV cache size and thus
            improve the model's throughput. However, if the value is too high, it may cause out-of-memory (OOM) errors
            during initialization.
        dtype (`str`, *optional*, defaults to `"auto"`):
            Data type to use for vLLM generation. If set to `"auto"`, the data type will be automatically determined
            based on the model configuration. Find the supported values in the vLLM documentation.
        max_model_len (`int` or `None`, *optional*, defaults to `None`):
            If set, the `max_model_len` to use for vLLM. This can be useful when running with reduced
            `vllm_gpu_memory_utilization`, leading to a reduced KV cache size. If not set, vLLM will use the model
            context size, which might be much larger than the KV cache, leading to inefficiencies.
        enable_prefix_caching (`bool` or `None`, *optional*, defaults to `None`):
            Whether to enable prefix caching in vLLM. If set to `True`, ensure that the model and the hardware support
            this feature.
        enforce_eager (`bool` or `None`, *optional*, defaults to `None`):
            Whether to enforce eager execution. If set to `True`, we will disable CUDA graph and always execute the
            model in eager mode. If `False` (default behavior), we will use CUDA graph and eager execution in hybrid.
        log_level (`str`, *optional*, defaults to `"info"`):
            Log level for uvicorn. Possible choices: `"critical"`, `"error"`, `"warning"`, `"info"`, `"debug"`,
            `"trace"`.
    """

    model: str = field(metadata={"help": "Model name or path to load the model from."})
    revision: Optional[str] = field(
        default=None,
        metadata={"help": "Revision to use for the model. If not specified, the default branch will be used."},
    )
    tensor_parallel_size: int = field(
        default=1,
        metadata={"help": "Number of tensor parallel workers to use."},
    )
    host: str = field(
        default="0.0.0.0",
        metadata={"help": "Host address to run the server on."},
    )
    port: int = field(
        default=8000,
        metadata={"help": "Port to run the server on."},
    )
    gpu_memory_utilization: float = field(
        default=0.9,
        metadata={
            "help": "Ratio (between 0 and 1) of GPU memory to reserve for the model weights, activations, and KV "
            "cache on the device dedicated to generation powered by vLLM. Higher values will increase the KV cache "
            "size and thus improve the model's throughput. However, if the value is too high, it may cause "
            "out-of-memory (OOM) errors during initialization."
        },
    )
    dtype: str = field(
        default="auto",
        metadata={
            "help": "Data type to use for vLLM generation. If set to 'auto', the data type will be automatically "
            "determined based on the model configuration. Find the supported values in the vLLM documentation."
        },
    )
    max_model_len: Optional[int] = field(
        default=None,
        metadata={
            "help": "If set, the `max_model_len` to use for vLLM. This can be useful when running with reduced "
            "`vllm_gpu_memory_utilization`, leading to a reduced KV cache size. If not set, vLLM will use the model "
            "context size, which might be much larger than the KV cache, leading to inefficiencies."
        },
    )
    enable_prefix_caching: Optional[bool] = field(
        default=None,
        metadata={
            "help": "Whether to enable prefix caching in vLLM. If set to `True`, ensure that the model and the "
            "hardware support this feature."
        },
    )
    enforce_eager: Optional[bool] = field(
        default=None,
        metadata={
            "help": "Whether to enforce eager execution. If set to `True`, we will disable CUDA graph and always "
            "execute the model in eager mode. If `False` (default behavior), we will use CUDA graph and eager "
            "execution in hybrid."
        },
    )
    log_level: str = field(
        default="info",
        metadata={
            "help": "Log level for uvicorn. Possible choices: 'critical', 'error', 'warning', 'info', 'debug', "
            "'trace'."
        },
    )


def main(script_args: ScriptArguments):
    if not is_fastapi_available():
        raise ImportError(
            "FastAPI is required to run the vLLM serve script. Please install it using `pip install fastapi`."
        )

    if not is_pydantic_available():
        raise ImportError(
            "Pydantic is required to run the vLLM serve script. Please install it using `pip install pydantic`."
        )

    if not is_uvicorn_available():
        raise ImportError(
            "Uvicorn is required to run the vLLM serve script. Please install it using `pip install uvicorn`."
        )

    if not is_vllm_available():
        raise ImportError("vLLM is required to run the vLLM serve script. Please install it using `pip install vllm`.")
    tokenizer = AutoTokenizer.from_pretrained(script_args.model)
    llm = LLM(
        model=script_args.model,
        revision=script_args.revision,
        tensor_parallel_size=script_args.tensor_parallel_size,
        gpu_memory_utilization=script_args.gpu_memory_utilization,
        enforce_eager=script_args.enforce_eager,
        dtype=script_args.dtype,
        # Automatic Prefix Caching caches the KV cache of existing queries, so that a new query can
        # directly reuse the KV cache if it shares the same prefix with one of the existing queries.
        # This is particularly useful here because we generate completions from the same prompts.
        enable_prefix_caching=script_args.enable_prefix_caching,
        max_model_len=script_args.max_model_len,
        worker_extension_cls="deepreasoningwithtools.samplers.vllm.vllm_server.WeightSyncWorkerExtension",
    )

    app = FastAPI()

    # Define the endpoints for the model server
    @app.get("/health/")
    async def health():
        """
        Health check endpoint to verify that the server is running.
        """
        return {"status": "ok"}

    @app.get("/get_tensor_parallel_size/")
    async def get_tensor_parallel_size():
        """
        Retrieves the tensor parallel size from the LLM engine.

        Returns:
            `dict`:
                A dictionary containing the tensor parallel size.

        Example response:
        ```json
        {"tensor_parallel_size": 8}
        ```
        """
        return {"tensor_parallel_size": llm.llm_engine.vllm_config.parallel_config.tensor_parallel_size}

    class GenerateRequest(BaseModel):
        prompt: list[str]
        n: int = 1
        repetition_penalty: float = 1.0
        temperature: float = 1.0
        top_p: float = 1.0
        top_k: int = -1
        min_p: float = 0.0
        max_tokens: int = 16
        guided_decoding_regex: Optional[str] = None

    class GenerateStreamingRequest(BaseModel):
        prompt: str
        n: int = 1
        repetition_penalty: float = 1.0
        temperature: float = 1.0
        top_p: float = 1.0
        top_k: int = -1
        min_p: float = 0.0
        max_tokens: int = 16
        guided_decoding_regex: Optional[str] = None
    
    class GenerateResponse(BaseModel):
        completion_ids: list[list[int]]

    def vllm_generate_iterator(
        prompt: str, sampling_params : SamplingParams, request_id: str, echo: bool = False, stop: str  = None, stop_token_ids: list[int] = None, 
    ) -> Iterator[StreamingResponseTokenT]:
        if request_id is None: raise ValueError('request_id must not be None.')
        if stop_token_ids is None: stop_token_ids = []
        stop_token_ids.append(tokenizer.eos_token_id)
        stop_ = set()
        if isinstance(stop, str) and stop != '': stop_.add(stop)
        elif isinstance(stop, list) and stop != []: stop_.update(stop)
        for tid in stop_token_ids:
            if tid: stop_.add(tokenizer.decode(tid))

        # if self.config['temperature'] <= 1e-5: top_p = 1.0
        # else: top_p = self.config['top_p']
        # config = self.config.model_construct_env(stop=list(stop_), top_p=top_p, **attrs)
        llm.llm_engine.add_request(request_id=request_id, prompt=prompt, params=sampling_params)

        token_cache = []
        print_len = 0
        text = ""
        while llm.llm_engine.has_unfinished_requests():
            for request_output in llm.llm_engine.step():
                # Add the new tokens to the cache
                if request_output.request_id != request_id:
                    continue # Skip if the request is not for this request_id
                for output in request_output.outputs:
                    text = output.text
                    yield StreamingResponseTokenT(text=text, 
                    error_code=0, 
                    num_tokens=len(output.token_ids), 
                    token_ids=output.token_ids, 
                    last_token_id=output.token_ids[-1],
                    last_token=tokenizer.decode(output.token_ids[-1]))

                if request_output.finished: 
                    break

    @app.post("/stream_generate/")
    def stream_generate(request: GenerateStreamingRequest):
        """
        Generates completions for the provided prompts.

        Args:
            request (`GenerateRequest`):
                - `prompts` (list of `str`): A list of prompts (text strings) for the model to generate completions.

        Returns:
            `GenerateResponse`:
                - `completion_ids` (list of list of `int`): A list of lists of token IDs for each generated completion.

        Example request:
        ```json
        {"prompts": ["Hello world", "What is AI?"]}
        ```

        Example response:
        ```json
        {"completion_ids": [[101, 102, 103], [201, 202, 203]]}
        ```
        """

        # Guided decoding, if enabled
        if request.guided_decoding_regex is not None:
            guided_decoding = GuidedDecodingParams(backend="outlines", regex=request.guided_decoding_regex)
        else:
            guided_decoding = None

        # Sampling parameters
        sampling_params = SamplingParams(
            n=request.n,
            repetition_penalty=request.repetition_penalty,
            temperature=request.temperature,
            top_p=request.top_p,
            top_k=request.top_k,
            min_p=request.min_p,
            max_tokens=request.max_tokens,  
            guided_decoding=guided_decoding,
            stop_token_ids=[tokenizer.eos_token_id],
        )
        request_id = str(uuid.uuid4())
        results_generator = vllm_generate_iterator(prompt=request.prompt, sampling_params=sampling_params, request_id=request_id)
        async def stream_results() -> AsyncGenerator[bytes, None]:
            for request_output in results_generator:
                yield (request_output.model_dump_json() + "\n").encode("utf-8")

        return StreamingResponse(stream_results())
    
    @app.post("/generate/", response_model=GenerateResponse)
    def generate(request: GenerateRequest):
        """
        Generates completions for the provided prompts.

        Args:
            request (`GenerateRequest`):
                - `prompts` (list of `str`): A list of prompts (text strings) for the model to generate completions.

        Returns:
            `GenerateResponse`:
                - `completion_ids` (list of list of `int`): A list of lists of token IDs for each generated completion.

        Example request:
        ```json
        {"prompts": ["Hello world", "What is AI?"]}
        ```

        Example response:
        ```json
        {"completion_ids": [[101, 102, 103], [201, 202, 203]]}
        ```
        """

        # Guided decoding, if enabled
        if request.guided_decoding_regex is not None:
            guided_decoding = GuidedDecodingParams(backend="outlines", regex=request.guided_decoding_regex)
        else:
            guided_decoding = None

        # Sampling parameters
        sampling_params = SamplingParams(
            n=request.n,
            repetition_penalty=request.repetition_penalty,
            temperature=request.temperature,
            top_p=request.top_p,
            top_k=request.top_k,
            min_p=request.min_p,
            max_tokens=request.max_tokens,
            guided_decoding=guided_decoding,
        )
        all_outputs = llm.generate(request.prompts, sampling_params=sampling_params)
        completion_ids = [list(output.token_ids) for outputs in all_outputs for output in outputs.outputs]
        return {"completion_ids": completion_ids}

   
    
    class InitCommunicatorRequest(BaseModel):
        host: str
        port: int
        world_size: int

    @app.post("/init_communicator/")
    async def init_communicator(request: InitCommunicatorRequest, background_tasks: BackgroundTasks):
        """
        Initializes the communicator for synchronizing model weights between a client and multiple server
        workers.

        Args:
            request (`InitCommunicatorRequest`):
                - `host` (`str`): Hostname or IP address of the master node.
                - `port` (`int`): Port number to be used for communication.
                - `world_size` (`int`): Total number of participating processes in the group.
        """
        print("4"*20 + "Initializing communicator" + "4"*20, script_args.tensor_parallel_size)
        background_tasks.add_task(
            llm.collective_rpc,
            "init_communicator",
            args=(request.host, request.port, script_args.tensor_parallel_size),
        )
        return {"message": "Request received, initializing communicator"}

    class UpdateWeightsRequest(BaseModel):
        name: str
        dtype: str
        shape: list[int]

    @app.post("/update_named_param/")
    async def update_named_param(request: UpdateWeightsRequest, background_tasks: BackgroundTasks):
        """
        Updates the model weights with the provided tensor.

        Once this endpoint is called, the client process should broadcast the updated weights to all server workers.

        Args:
            request (`UpdateWeightsRequest`):
                - `name` (`str`): Name of the weight tensor being updated.
                - `dtype` (`str`): Data type of the weight tensor (e.g., `"torch.float32"`).
                - `shape` (list of `int`): Shape of the weight

        """
        # The function is called this way: update_named_param(name="name", dtype=torch.float32, shape=(10, 10))
        # So with collect_rpc we need to call it this way:
        # llm.collective_rpc("update_named_param", args=("name", torch.float32, (10, 10)))
        # And with background_tasks.add_task we need to call it this way:
        # background_tasks.add_task(llm.collective_rpc, "update_named_param", args=("name", torch.float32, (10, 10)))
        dtype = torch.__getattribute__(request.dtype.split(".")[-1])
        background_tasks.add_task(llm.collective_rpc, "update_named_param", args=(request.name, dtype, request.shape))

        return {"message": "Request received, updating named parameter"}

    @app.post("/reset_prefix_cache/")
    async def reset_prefix_cache():
        """
        Resets the prefix cache for the model.
        """
        success = llm.llm_engine.reset_prefix_cache()
        return {"message": "Request received, resetting prefix cache status: " + str(success)}

    @app.post("/close_communicator/")
    async def close_communicator():
        """
        Closes the weight update group and cleans up associated resources.
        """
        llm.collective_rpc("close_communicator")
        return {"message": "Request received, closing communicator"}

    # Start the server
    uvicorn.run(app, host=script_args.host, port=script_args.port, log_level=script_args.log_level)


def make_parser(subparsers: argparse._SubParsersAction = None):
    if subparsers is not None:
        parser = subparsers.add_parser("vllm-serve", help="Run the vLLM serve script", dataclass_types=ScriptArguments)
    else:
        parser = CLIParser(ScriptArguments)
    return parser


def cli_main():
    parser = make_parser()
    (script_args,) = parser.parse_args_and_config()
    main(script_args)

if __name__ == "__main__":
    parser = make_parser()
    (script_args,) = parser.parse_args_and_config()
    main(script_args)
