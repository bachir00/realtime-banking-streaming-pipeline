import json
import os
import random
import time
from datetime import datetime
from kafka import KafkaProducer

KAFKA_BROKERS = os.environ.get('KAFKA_BROKERS', '')
KAFKA_TOPIC = os.environ.get('KAFKA_TOPIC', 'transactions')
TRANSACTION_INTERVAL = float(os.environ.get('TRANSACTION_INTERVAL_SEC', '1'))

MERCHANTS = ['Amazon', 'Walmart', 'Starbucks', 'McDonald', 'Apple', 'Target']
LOCATIONS = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix']
TRANSACTION_TYPES = ['online', 'offline', 'atm']


def generate_transaction():
    return {
        'transaction_id': random.randint(1, 2_000_000_000),
        'account_id': random.randint(1000, 9999),
        'amount': round(random.uniform(10, 5000), 2),
        'merchant': random.choice(MERCHANTS),
        'timestamp': datetime.now().isoformat(),
        'location': random.choice(LOCATIONS),
        'transaction_type': random.choice(TRANSACTION_TYPES),
    }


def create_producer():
    for attempt in range(30):
        try:
            print(f"Tentative de connexion {attempt + 1}/30...")
            producer = KafkaProducer(
                bootstrap_servers=KAFKA_BROKERS,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                request_timeout_ms=5000
            )
            print("✓ Connecté à Kafka!")
            return producer
        except Exception as e:
            print(f"Erreur: {e}")
            if attempt < 29:
                time.sleep(1)
    return None


def main():
    producer = create_producer()
    if not producer:
        print("Impossible de se connecter à Kafka après 30 tentatives")
        return

    print(f"Producer démarré — topic: {KAFKA_TOPIC}, interval: {TRANSACTION_INTERVAL}s")
    count = 0

    try:
        while True:
            transaction = generate_transaction()
            try:
                future = producer.send(KAFKA_TOPIC, value=transaction)
                future.get(timeout=5)
                count += 1
                if count % 5 == 0:
                    print(f"✓ {count} transactions produites")
            except Exception as e:
                print(f"Erreur d'envoi: {e}")
            time.sleep(TRANSACTION_INTERVAL)
    except KeyboardInterrupt:
        print("\nProducer arrêté")
    finally:
        producer.close()


if __name__ == '__main__':
    main()
