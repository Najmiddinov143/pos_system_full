FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Kerakli asosiy kutubxonalarni kafolatlangan holda o'rnatamiz
RUN pip install --no-cache-dir -r requirements.txt fastapi uvicorn asyncpg pydantic gunicorn

COPY . .

CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "10000"]
