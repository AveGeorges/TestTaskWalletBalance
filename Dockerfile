FROM python:3.12-slim

WORKDIR /app

# Системные зависимости для psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY req.txt .
RUN pip install --no-cache-dir -r req.txt

COPY . .

RUN chmod +x /app/scripts/entrypoint.sh

# Порт FastAPI
EXPOSE 8000

ENTRYPOINT ["/app/scripts/entrypoint.sh"]