import json
import random
import time
from datetime import datetime
from kafka import KafkaProducer

# Configuration Kafka
KAFKA_BROKERS = ['kafka:9092']
KAFKA_TOPIC = 'transactions'

def generate_fake_transaction():
    """Génère une transaction bancaire fake"""
    transaction = {
        'transaction_id': random.randint(100000, 999999),
        'account_id': random.randint(1000, 9999),
        'amount': round(random.uniform(10, 5000), 2),
        'merchant': random.choice(['Amazon', 'Walmart', 'Starbucks', 'McDonald', 'Apple', 'Target']),
        'timestamp': datetime.now().isoformat(),
        'location': random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix']),
        'transaction_type': random.choice(['online', 'offline', 'atm']),
    }
    return transaction

def main():
    """Produit les transactions vers Kafka"""
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    
    print("Producer démarré. Génération de transactions...")
    
    try:
        while True:
            transaction = generate_fake_transaction()
            producer.send(KAFKA_TOPIC, value=transaction)
            print(f"Transaction produite: {transaction['transaction_id']}")
            time.sleep(1)  # Une transaction par seconde
    except KeyboardInterrupt:
        print("Producer arrêté")
    finally:
        producer.close()

if __name__ == '__main__':
    main()
