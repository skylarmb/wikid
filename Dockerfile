FROM python:3.12-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
RUN uv pip install --system vllm --torch-backend=auto
