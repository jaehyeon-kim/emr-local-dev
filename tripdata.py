import sys
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql.functions import lit

if __name__ == "__main__":
    spark = SparkSession.builder.appName("Trip Data").enableHiveSupport().getOrCreate()

    dbname = "tripdata"
    tblname = "ny_taxi"
    dest_path = "s3://emr-local-dev/tripdata/"
    # src_path = "s3://nyc-tlc/trip data/yellow_tripdata_2020-04.csv"
    src_path = "s3://aws-data-analytics-workshops/shared_datasets/tripdata/"
    ny_taxi = spark.read.option("inferSchema", "true").option("header", "true").csv(src_path)
    ny_taxi = ny_taxi.withColumn("created_at", lit(datetime.now()))
    ny_taxi.printSchema()

    ny_taxi.write.mode("overwrite").parquet(dest_path)

    ny_taxi.registerTempTable(tblname)
    spark.sql(f"CREATE DATABASE IF NOT EXISTS {dbname}")
    spark.sql(f"USE {dbname}")
    spark.sql(
        f"""CREATE TABLE IF NOT EXISTS {tblname} 
            USING PARQUET 
            LOCATION '{dest_path}'
            AS SELECT * FROM {tblname}
        """
    )
