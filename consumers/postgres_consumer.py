import json
import os
import time
from kafka import KafkaConsumer
import psycopg2

print("=== Starting Consumer ===", flush=True)

KAFKA_BROKERS = os.environ.get('KAFKA_BROKERS', 'localhost:9092')
KAFKA_TOPIC = os.environ.get('KAFKA_TOPIC', 'transactions')
KAFKA_GROUP_ID = os.environ.get('KAFKA_GROUP_ID', 'postgres-consumer-group')
KAFKA_AUTO_OFFSET_RESET = os.environ.get('KAFKA_AUTO_OFFSET_RESET', 'latest')

DB_HOST = os.environ.get('DB_HOST', '')
DB_PORT = int(os.environ.get('DB_PORT', ''))
DB_NAME = os.environ.get('DB_NAME', '')
DB_USER = os.environ.get('DB_USER', '')
DB_PASSWORD = os.environ.get('DB_PASSWORD', '')

INSERT_QUERY = """
    INSERT INTO transactions
        (transaction_id, account_id, amount, merchant, timestamp, location, transaction_type)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (transaction_id) DO NOTHING;
"""


def connect_postgres():
    for attempt in range(30):
        try:
            print(f"  PostgreSQL attempt {attempt + 1}/30...", flush=True)
            conn = psycopg2.connect(
                host=DB_HOST, port=DB_PORT,
                database=DB_NAME, user=DB_USER, password=DB_PASSWORD
            )
            print("✓ Connected to PostgreSQL!", flush=True)
            return conn
        except Exception as e:
            print(f"  Error: {e}", flush=True)
            if attempt < 29:
                time.sleep(1)
    return None


def connect_kafka():
    for attempt in range(30):
        try:
            print(f"  Kafka attempt {attempt + 1}/30...", flush=True)
            consumer = KafkaConsumer(
                KAFKA_TOPIC,
                bootstrap_servers=KAFKA_BROKERS,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                auto_offset_reset=KAFKA_AUTO_OFFSET_RESET,
                enable_auto_commit=True,
                group_id=KAFKA_GROUP_ID
            )
            print("✓ Connected to Kafka!", flush=True)
            return consumer
        except Exception as e:
            print(f"  Error: {e}", flush=True)
            if attempt < 29:
                time.sleep(1)
    return None


def main():
    print("Connecting to PostgreSQL...", flush=True)
    db_conn = connect_postgres()
    if not db_conn:
        print("✗ Cannot connect to PostgreSQL after 30 attempts", flush=True)
        raise SystemExit(1)

    print("Connecting to Kafka...", flush=True)
    consumer = connect_kafka()
    if not consumer:
        print("✗ Cannot connect to Kafka after 30 attempts", flush=True)
        db_conn.close()
        raise SystemExit(1)

    print(f"Waiting for transactions on topic '{KAFKA_TOPIC}'...", flush=True)
    count = 0

    try:
        for message in consumer:
            transaction = message.value
            print(f"Received: {transaction['transaction_id']}", flush=True)
            try:
                cursor = db_conn.cursor()
                cursor.execute(INSERT_QUERY, (
                    transaction['transaction_id'],
                    transaction['account_id'],
                    transaction['amount'],
                    transaction['merchant'],
                    transaction['timestamp'],
                    transaction['location'],
                    transaction['transaction_type']
                ))
                db_conn.commit()
                cursor.close()
                count += 1
                if count % 5 == 0:
                    print(f"✓ Saved {count} transactions total", flush=True)
            except Exception as e:
                print(f"✗ Error saving transaction: {e}", flush=True)
                db_conn.rollback()
    except KeyboardInterrupt:
        print("\nConsumer stopped", flush=True)
    finally:
        consumer.close()
        db_conn.close()
        print("Connections closed", flush=True)


if __name__ == '__main__':
    main()
