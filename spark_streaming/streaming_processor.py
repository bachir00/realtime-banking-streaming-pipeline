import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType

KAFKA_BROKERS = os.environ.get('KAFKA_BROKERS', '')
KAFKA_TOPIC = os.environ.get('KAFKA_TOPIC', 'transactions')

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
    .appName("BankingStreamingProcessor") \
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

df_parsed = df_parsed.withColumn(
    "event_time",
    col("timestamp").cast("timestamp")
)

query = df_parsed \
    .writeStream \
    .outputMode("append") \
    .format("console") \
    .option("truncate", "false") \
    .start()

query.awaitTermination()
