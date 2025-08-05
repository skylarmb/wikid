#!/usr/bin/env python3
"""
Web server that runs vLLM API and serves the frontend.
"""

import argparse
import asyncio
import os
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn


class VLLMServerManager:
    def __init__(self):
        self.process = None
        self.running = False
    
    def start_vllm(
        self,
        model_name: str,
        host: str,
        port: int,
        api_key: Optional[str],
        dtype: str,
        max_model_len: Optional[int],
        tensor_parallel_size: int,
        gpu_memory_utilization: float,
    ):
        cmd = [
            "vllm", "serve", model_name,
            "--host", host,
            "--port", str(port),
            "--dtype", dtype,
            "--tensor-parallel-size", str(tensor_parallel_size),
            "--gpu-memory-utilization", str(gpu_memory_utilization),
        ]
        
        if api_key:
            cmd.extend(["--api-key", api_key])
        
        if max_model_len:
            cmd.extend(["--max-model-len", str(max_model_len)])
        
        print(f"Starting vLLM server: {' '.join(cmd)}")
        
        self.process = subprocess.Popen(cmd)
        self.running = True
        
        # Wait a bit for server to start
        time.sleep(3)
        
        return self.process
    
    def stop(self):
        if self.process and self.running:
            self.process.terminate()
            self.process.wait()
            self.running = False


def create_web_app(vllm_host: str, vllm_port: int) -> FastAPI:
    app = FastAPI(title="Qwen Server with Frontend")
    
    # Get the frontend directory
    frontend_dir = Path(__file__).parent.parent / "frontend"
    
    @app.get("/", response_class=HTMLResponse)
    async def serve_frontend():
        frontend_file = frontend_dir / "index.html"
        if frontend_file.exists():
            with open(frontend_file, "r") as f:
                content = f.read()
            # Update the default server URL in the HTML
            content = content.replace(
                'value="http://localhost:8000"',
                f'value="http://{vllm_host}:{vllm_port}"'
            )
            return HTMLResponse(content)
        else:
            return HTMLResponse("<h1>Frontend not found</h1><p>Please ensure frontend/index.html exists</p>")
    
    @app.get("/health")
    async def health_check():
        return {"status": "ok", "vllm_endpoint": f"http://{vllm_host}:{vllm_port}"}
    
    return app


def start_web_server(
    model_name: str = "qwen-community/Qwen3-8B-FP8",
    vllm_host: str = "127.0.0.1",
    vllm_port: int = 8000,
    web_host: str = "0.0.0.0",
    web_port: int = 8080,
    api_key: Optional[str] = None,
    dtype: str = "auto",
    max_model_len: Optional[int] = 21904,
    tensor_parallel_size: int = 1,
    gpu_memory_utilization: float = 0.85,
) -> None:
    """Start both vLLM server and web server."""
    
    vllm_manager = VLLMServerManager()
    
    try:
        # Start vLLM in background
        print("Starting vLLM server...")
        vllm_manager.start_vllm(
            model_name=model_name,
            host=vllm_host,
            port=vllm_port,
            api_key=api_key,
            dtype=dtype,
            max_model_len=max_model_len,
            tensor_parallel_size=tensor_parallel_size,
            gpu_memory_utilization=gpu_memory_utilization,
        )
        
        # Create and start web server
        print(f"Starting web server at http://{web_host}:{web_port}")
        app = create_web_app(vllm_host, vllm_port)
        
        uvicorn.run(
            app,
            host=web_host,
            port=web_port,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        print("\nShutting down servers...")
    finally:
        vllm_manager.stop()


def main():
    parser = argparse.ArgumentParser(
        description="Start vLLM server with web frontend"
    )
    parser.add_argument(
        "--model",
        default="qwen-community/Qwen3-8B-FP8",
        help="Model name to serve"
    )
    parser.add_argument(
        "--vllm-host",
        default="127.0.0.1",
        help="vLLM server host (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--vllm-port",
        type=int,
        default=8000,
        help="vLLM server port (default: 8000)"
    )
    parser.add_argument(
        "--web-host",
        default="0.0.0.0",
        help="Web server host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--web-port",
        type=int,
        default=8080,
        help="Web server port (default: 8080)"
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
        default=21904,
        help="Maximum model length (default: 21904)"
    )
    parser.add_argument(
        "--tensor-parallel-size",
        type=int,
        default=1,
        help="Number of GPUs for tensor parallelism (default: 1)"
    )
    parser.add_argument(
        "--gpu-memory-utilization",
        type=float,
        default=0.85,
        help="GPU memory utilization ratio (default: 0.85)"
    )
    
    args = parser.parse_args()
    
    start_web_server(
        model_name=args.model,
        vllm_host=args.vllm_host,
        vllm_port=args.vllm_port,
        web_host=args.web_host,
        web_port=args.web_port,
        api_key=args.api_key,
        dtype=args.dtype,
        max_model_len=args.max_model_len,
        tensor_parallel_size=args.tensor_parallel_size,
        gpu_memory_utilization=args.gpu_memory_utilization,
    )


if __name__ == "__main__":
    main()