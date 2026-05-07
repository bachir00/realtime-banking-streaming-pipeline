FROM bitnami/spark:3.3.0

WORKDIR /app

COPY ../requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY streaming_processor.py .
COPY fraud_detector.py .

CMD ["spark-submit", "--packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0", "streaming_processor.py"]
