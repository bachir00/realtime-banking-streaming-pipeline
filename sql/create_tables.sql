-- Créer la table des transactions
CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    transaction_id INTEGER UNIQUE NOT NULL,
    account_id INTEGER NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    merchant VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    location VARCHAR(100),
    transaction_type VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Créer un index sur account_id pour les performances
CREATE INDEX idx_account_id ON transactions(account_id);
CREATE INDEX idx_timestamp ON transactions(timestamp);

-- Créer une table pour les anomalies détectées
CREATE TABLE IF NOT EXISTS fraud_alerts (
    id SERIAL PRIMARY KEY,
    transaction_id INTEGER NOT NULL,
    account_id INTEGER NOT NULL,
    amount DECIMAL(10, 2),
    alert_reason VARCHAR(255),
    alert_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id)
);

-- Créer un index sur fraud_alerts
CREATE INDEX idx_fraud_alerts_timestamp ON fraud_alerts(alert_timestamp);
