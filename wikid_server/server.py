#!/usr/bin/env python3
"""
Simple vLLM server for offline research assistant models.
"""

import argparse
import subprocess
import sys
from typing import Optional


DEFAULT_MODEL = "Qwen/Qwen3-8B-FP8"
DEFAULT_MEM_UTIL = 0.85

def start_server(
    model_name: str = DEFAULT_MODEL,
    host: str = "0.0.0.0",
    port: int = 8000,
    api_key: Optional[str] = None,
    dtype: str = "auto",
    max_model_len: Optional[int] = 8192,
    tensor_parallel_size: int = 1,
    gpu_memory_utilization: float = DEFAULT_MEM_UTIL,
) -> None:
    """Start the vLLM OpenAI-compatible server."""

    cmd = [
        "vllm", "serve", model_name,
        "--host", host,
        "--port", str(port),
        "--dtype", dtype,
        "--tensor-parallel-size", str(tensor_parallel_size),
        "--gpu-memory-utilization", str(gpu_memory_utilization),
        "--enable-auto-tool-choice",
        "--tool-call-parser", "hermes",
    ]

    if api_key:
        cmd.extend(["--api-key", api_key])

    if max_model_len:
        cmd.extend(["--max-model-len", str(max_model_len)])

    print(f"Starting vLLM server for {model_name}...")
    print(f"Server will be available at http://{host}:{port}")
    print(f"Command: {' '.join(cmd)}")

    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\nServer stopped by user.")
    except subprocess.CalledProcessError as e:
        print(f"Error starting server: {e}")
        sys.exit(1)


def main():
    """Main entry point for the server."""
    parser = argparse.ArgumentParser(
        description="Start vLLM server for offline research assistant models"
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help="Model name to serve, default: " + DEFAULT_MODEL
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)"
    )
    parser.add_argument(
        "--api-key",
        help="API key for authentication"
    )
    parser.add_argument(
        "--dtype",
        default="auto",
        help="Data type for model weights (default: auto)"
    )
    parser.add_argument(
        "--max-model-len",
        type=int,
        default=8192,
        help="Maximum model length (default: 8192, matches Hermes model max_position_embeddings)"
    )
    parser.add_argument(
        "--tensor-parallel-size",
        type=int,
        default=1,
        help="Number of GPUs to use for tensor parallelism (default: 1)"
    )
    parser.add_argument(
        "--gpu-memory-utilization",
        type=float,
        default=DEFAULT_MEM_UTIL,
        help="GPU memory utilization ratio, default: 0.85"
    )

    args = parser.parse_args()

    start_server(
        model_name=args.model,
        host=args.host,
        port=args.port,
        api_key=args.api_key,
        dtype=args.dtype,
        max_model_len=args.max_model_len,
        tensor_parallel_size=args.tensor_parallel_size,
        gpu_memory_utilization=args.gpu_memory_utilization,
    )


if __name__ == "__main__":
    main()
