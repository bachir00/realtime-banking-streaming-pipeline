import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, when
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType

KAFKA_BROKERS = os.environ.get('KAFKA_BROKERS', '')
KAFKA_TOPIC = os.environ.get('KAFKA_TOPIC', 'transactions')
FRAUD_THRESHOLD = float(os.environ.get('FRAUD_AMOUNT_THRESHOLD', '3000'))
HIGH_VALUE_THRESHOLD = float(os.environ.get('HIGH_VALUE_THRESHOLD', '4000'))

DB_HOST = os.environ.get('POSTGRES_HOST', '')
DB_PORT = os.environ.get('POSTGRES_PORT', '5432')
DB_NAME = os.environ.get('POSTGRES_DB', '')
DB_USER = os.environ.get('POSTGRES_USER', '')
DB_PASSWORD = os.environ.get('POSTGRES_PASSWORD', '')

POSTGRES_URL = f"jdbc:postgresql://{DB_HOST}:{DB_PORT}/{DB_NAME}"
POSTGRES_PROPERTIES = {
    "user": DB_USER,
    "password": DB_PASSWORD,
    "driver": "org.postgresql.Driver"
}

SCHEMA = StructType([
    StructField("transaction_id", IntegerType()),
    StructField("account_id", IntegerType()),
    StructField("amount", DoubleType()),
    StructField("merchant", StringType()),
    StructField("timestamp", StringType()),
    StructField("location", StringType()),
    StructField("transaction_type", StringType()),
])

spark = SparkSession \
    .builder \
    .appName("FraudDetector") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

df_transactions = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BROKERS) \
    .option("subscribe", KAFKA_TOPIC) \
    .load()

df_parsed = df_transactions.select(
    from_json(col("value").cast("string"), SCHEMA).alias("data")
).select("data.*")

df_fraud = df_parsed \
    .filter(col("amount") > FRAUD_THRESHOLD) \
    .select(
        col("transaction_id"),
        col("account_id"),
        col("amount"),
        when(col("amount") > HIGH_VALUE_THRESHOLD, f"High value transaction > {HIGH_VALUE_THRESHOLD}")
            .otherwise(f"Suspicious transaction > {FRAUD_THRESHOLD}").alias("alert_reason")
    )


def write_to_postgres(batch_df, batch_id):
    if not batch_df.isEmpty():
        batch_df.write.jdbc(
            url=POSTGRES_URL,
            table="fraud_alerts",
            mode="append",
            properties=POSTGRES_PROPERTIES
        )
        print(f"Batch {batch_id}: {batch_df.count()} fraud alerts saved", flush=True)


query = df_fraud \
    .writeStream \
    .outputMode("append") \
    .foreachBatch(write_to_postgres) \
    .start()

query.awaitTermination()
