# Real-time Banking Streaming Pipeline

Pipeline temps réel pour le traitement et l'analyse des transactions bancaires utilisant Kafka, Spark Streaming et PostgreSQL.

## Architecture

```
┌─────────────────┐
│    Producer     │ (Génère des transactions fake)
│   Kafka Topic   │
└────────┬────────┘
         │
         ├─────────────────────┬─────────────────────┐
         │                     │                     │
    ┌────▼────────┐   ┌────────▼────┐  ┌─────────────▼────┐
    │   Spark     │   │  Fraud      │  │  PostgreSQL      │
    │ Streaming   │   │  Detector   │  │   Consumer       │
    │ Processor   │   └─────────────┘  └──────┬───────────┘
    └─────────────┘                           │
                               ┌──────────────▼─────────────┐
                               │       PostgreSQL DB        │
                               │  - Transactions            │
                               │  - Fraud Alerts            │
                               └─────────────┬──────────────┘
                                             │
                               ┌─────────────▼──────────────┐
                               │       Grafana              │
                               │   (Dashboards & Alertes)   │
                               └────────────────────────────┘
```

## Prérequis

- Docker
- Docker Compose
- Python 3.9+

## Installation

### 1. Cloner le repository
```bash
cd realtime-banking-streaming-pipeline
```

### 2. Démarrer les services
```bash
docker-compose up -d
```

### 3. Vérifier que tous les services sont lancés
```bash
docker-compose ps
```

## Services

### 1. **Kafka** (Port 9092)
- Message broker pour le streaming de transactions
- Topic: `transactions`

### 2. **PostgreSQL** (Port 5432)
- Base de données pour la persistance
- Credentials: postgres/password

### 3. **Spark** (Master: 8080, Worker: 7077)
- Traitement et analyse des streams
- Détection d'anomalies

### 4. **Grafana** (Port 3000)
- Dashboards temps réel
- Login: admin/admin

## Fichiers principaux

- **producer/transaction_producer.py**: Génère des transactions bancaires
- **spark_streaming/streaming_processor.py**: Traitement Spark Streaming
- **spark_streaming/fraud_detector.py**: Détection d'anomalies
- **consumers/postgres_consumer.py**: Sauvegarde dans PostgreSQL
- **sql/create_tables.sql**: Schéma de base de données
- **grafana/dashboard.json**: Dashboard préconfigué

## Utilisation

### Vérifier les transactions
```bash
docker-compose logs -f producer
```

### Consulter la base de données
```bash
docker-compose exec postgres psql -U postgres -d banking_db
```

### Accéder aux interfaces web
- Grafana: http://localhost:3000
- Spark Master: http://localhost:8080

## Arrêter les services
```bash
docker-compose down -v
```

## Notes

- Le pipeline génère 1 transaction par seconde
- Les transactions avec montant > 3000 sont marquées comme suspects
- Les données sont persistées dans PostgreSQL

## Améliorations futures

- Implémentation d'algorithmes ML plus avancés pour la détection de fraude
- Intégration avec des services d'alertes
- Monitoring et logging améliorés
- Scalabilité horizontale
