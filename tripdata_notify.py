from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_json, struct
from utils import remove_checkpoint

if __name__ == "__main__":
    remove_checkpoint()

    spark = (
        SparkSession.builder.appName("Trip Data Notification")
        .config("spark.streaming.stopGracefullyOnShutdown", "true")
        .config("spark.sql.shuffle.partitions", 3)
        .getOrCreate()
    )

    tripdata_ddl = """
    record_id STRING,
    VendorID STRING,
    lpep_pickup_datetime STRING,
    lpep_dropoff_datetime STRING,
    store_and_fwd_flag STRING,
    RatecodeID STRING,
    PULocationID STRING,
    DOLocationID STRING,
    passenger_count STRING,
    trip_distance STRING,
    fare_amount STRING,
    extra STRING,
    mta_tax STRING,
    tip_amount STRING,
    tolls_amount STRING,
    ehail_fee STRING,
    improvement_surcharge STRING,
    total_amount STRING,
    payment_type STRING,
    trip_type STRING
    """

    ny_taxi = (
        spark.readStream.format("json")
        .option("path", "data/json")
        .option("maxFilesPerTrigger", "1000")
        .schema(tripdata_ddl)
        .load()
    )

    target_df = ny_taxi.filter(col("total_amount") < 0).select(
        col("record_id").alias("key"), to_json(struct("*")).alias("value")
    )

    notification_writer_query = (
        target_df.writeStream.format("kafka")
        .queryName("notifications")
        .option("kafka.bootstrap.servers", "kafka:9092")
        .option("topic", "notifications")
        .outputMode("append")
        .option("checkpointLocation", ".checkpoint")
        .start()
    )

    notification_writer_query.awaitTermination()
