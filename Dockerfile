FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Render o'zi beradigan $PORT o'zgaruvchisidan foydalanamiz
CMD uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}
