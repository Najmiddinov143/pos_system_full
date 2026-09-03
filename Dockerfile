FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# uvicorn va gunicorn o'rnatilishini aniq ko'rsatamiz
RUN pip install --no-cache-dir -r requirements.txt uvicorn gunicorn

COPY . .

# Array formatida (Exec form) ishga tushiramiz
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "10000"]
