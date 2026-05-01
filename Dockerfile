FROM python:3.11.11

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

COPY frontend/ ./frontend/
COPY src/ ./src/
COPY mediapipe/ ./mediapipe/

RUN uv sync --frozen

WORKDIR /app/frontend

EXPOSE 80

CMD ["uv", "run", "fastapi", "run", "main.py", "--port", "80", "--host", "0.0.0.0"]
