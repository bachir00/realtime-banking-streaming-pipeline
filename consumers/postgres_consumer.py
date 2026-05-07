import json
import psycopg2
from kafka import KafkaConsumer
from datetime import datetime

# Configuration PostgreSQL
DB_HOST = 'postgres'
DB_PORT = 5432
DB_NAME = 'banking_db'
DB_USER = 'postgres'
DB_PASSWORD = 'password'

# Configuration Kafka
KAFKA_BROKERS = ['kafka:9092']
KAFKA_TOPIC = 'transactions'

def save_transaction(transaction):
    """Sauvegarde une transaction dans PostgreSQL"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()
        
        query = """
        INSERT INTO transactions 
        (transaction_id, account_id, amount, merchant, timestamp, location, transaction_type, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        values = (
            transaction['transaction_id'],
            transaction['account_id'],
            transaction['amount'],
            transaction['merchant'],
            transaction['timestamp'],
            transaction['location'],
            transaction['transaction_type'],
            datetime.now()
        )
        
        cursor.execute(query, values)
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"Transaction sauvegardée: {transaction['transaction_id']}")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde: {e}")

def main():
    """Consomme les transactions depuis Kafka et les sauvegarde"""
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BROKERS,
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='earliest'
    )
    
    print("Consumer PostgreSQL démarré...")
    
    try:
        for message in consumer:
            transaction = message.value
            save_transaction(transaction)
    except KeyboardInterrupt:
        print("Consumer arrêté")
    finally:
        consumer.close()

if __name__ == '__main__':
    main()
