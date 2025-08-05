# wikid 📚

An offline research assistant powered by vLLM and ZIM files. Because sometimes you want to ask Wikipedia questions without the internet.

## What is this?

A fun side project that lets you chat with an AI that can search through offline knowledge bases (Wikipedia, Stack Exchange, etc.) stored as ZIM files. Built with vLLM for fast local inference and 100% vibe-coded with Claude.

## Quick Start

```bash
# Install dependencies
uv sync

# Start the vLLM server (in one terminal)
uv run qwen-server

# Chat with your offline assistant (in another terminal)
uv run qwen-chat
```

## What's in the box?

- 🤖 Local AI assistant using Qwen3-8B-FP8 (16gb vram required, or swap in your own model)
- 📁 Offline knowledge search through ZIM files
- 💬 Interactive chat with streaming responses
- 🎨 Markdown rendering in your terminal
- 🔧 Tool calling for research tasks

## Current Status

Basic infrastructure is done. Working on ZIM file integration next. See `PROJECT.md` for the full roadmap.

## Why?

The goal was to experiment with function calling / tool use using local models and create a reliable AI assistant that could provide factual information even in a completely off-grid / offline / zombie apocalypse scenario. Because when the internet goes down, you still need to know how to configure systemd services! 🧟‍♂️
