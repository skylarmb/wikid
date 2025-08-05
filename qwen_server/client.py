#!/usr/bin/env python3
"""
Simple client example for the Qwen3-8B-FP8 vLLM server.
"""

import argparse
from openai import OpenAI
from typing import Optional


def create_client(base_url: str = "http://localhost:8000/v1", api_key: Optional[str] = None) -> OpenAI:
    """Create an OpenAI client for the vLLM server."""
    return OpenAI(
        base_url=base_url,
        api_key=api_key or "dummy-key"
    )


def chat_completion(
    client: OpenAI,
    message: str,
    model: str = "qwen-community/Qwen3-8B-FP8",
    max_tokens: int = 512,
    temperature: float = 0.7,
) -> str:
    """Send a chat completion request."""
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": message}
        ],
        max_tokens=max_tokens,
        temperature=temperature,
    )
    
    return response.choices[0].message.content


def main():
    """Main entry point for the client."""
    parser = argparse.ArgumentParser(
        description="Simple client for Qwen3-8B-FP8 vLLM server"
    )
    parser.add_argument(
        "message",
        help="Message to send to the model"
    )
    parser.add_argument(
        "--base-url",
        default="http://localhost:8000/v1",
        help="Base URL for the vLLM server (default: http://localhost:8000/v1)"
    )
    parser.add_argument(
        "--api-key",
        help="API key for authentication"
    )
    parser.add_argument(
        "--model",
        default="qwen-community/Qwen3-8B-FP8",
        help="Model name (default: qwen-community/Qwen3-8B-FP8)"
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=512,
        help="Maximum tokens in response (default: 512)"
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.7,
        help="Temperature for sampling (default: 0.7)"
    )
    
    args = parser.parse_args()
    
    try:
        client = create_client(args.base_url, args.api_key)
        response = chat_completion(
            client,
            args.message,
            args.model,
            args.max_tokens,
            args.temperature,
        )
        print(response)
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()