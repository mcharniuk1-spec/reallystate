FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential curl libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY src ./src
COPY tests ./tests
COPY data ./data
COPY sql ./sql

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -e ".[dev]"

CMD ["python", "-m", "unittest", "discover", "-s", "tests", "-v"]
