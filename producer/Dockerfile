FROM python:3.9-slim

WORKDIR /app

COPY ../requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY transaction_producer.py .

CMD ["python", "transaction_producer.py"]
