FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

ENV UV_COMPILE_BYTECODE=1
ENV UV_NO_CACHE=1

RUN apt update && \
    apt install -y --no-install-recommends \
    build-essential \
    cmake \
    curl \
    gcc \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /src
COPY README.md /src/
COPY pyproject.toml /src/
RUN uv sync --no-dev
COPY src/opensymbiose /src/opensymbiose

EXPOSE 7860

ENV PYTHONPATH=/src
ENV GRADIO_SERVER_NAME=0.0.0.0
CMD ["uv", "run", "gradio", "/src/opensymbiose/gradio/app.py"]
