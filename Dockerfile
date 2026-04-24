FROM python:3.11.11

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

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY frontend/ ./frontend/
COPY src/ ./src/

WORKDIR /app/frontend

EXPOSE 8000

ENTRYPOINT ["fastapi", "dev", "main.py", "--host", "0.0.0.0"]
