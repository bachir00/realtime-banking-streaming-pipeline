FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY consumers/postgres_consumer.py .

CMD ["python", "-u", "postgres_consumer.py"]
