from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, schema_of_json, window, count
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType
import json

# Initialiser SparkSession
spark = SparkSession \
    .builder \
    .appName("BankingStreamingProcessor") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# Schéma des transactions
schema = StructType([
    StructField("transaction_id", IntegerType()),
    StructField("account_id", IntegerType()),
    StructField("amount", DoubleType()),
    StructField("merchant", StringType()),
    StructField("timestamp", StringType()),
    StructField("location", StringType()),
    StructField("transaction_type", StringType()),
])

# Lire depuis Kafka
df_transactions = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "transactions") \
    .load()

# Parser les données JSON
df_parsed = df_transactions.select(
    from_json(col("value").cast("string"), schema).alias("data")
).select("data.*")

# Ajouter colonne de timestamp pour les opérations temporelles
df_parsed = df_parsed.withColumn(
    "event_time",
    col("timestamp").cast("timestamp")
)

# Afficher le stream pour debug
query = df_parsed \
    .writeStream \
    .outputMode("append") \
    .format("console") \
    .start()

query.awaitTermination()
