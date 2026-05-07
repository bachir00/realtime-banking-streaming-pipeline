FROM apache/spark:3.4.0-python3

USER root

RUN mkdir -p /home/spark/.ivy2/cache /home/spark/.ivy2/jars \
    && chown -R spark:spark /home/spark

COPY spark_streaming/fraud_detector.py /app/fraud_detector.py
COPY spark_streaming/streaming_processor.py /app/streaming_processor.py

USER spark

CMD ["/opt/spark/bin/spark-submit", \
     "--master", "local[*]", \
     "--packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.0,org.postgresql:postgresql:42.6.0", \
     "/app/fraud_detector.py"]
