import sys
from pyspark.sql import SparkSession

from utils import to_timestamp_df

if __name__ == "__main__":
    spark = SparkSession.builder.appName("Trip Data").getOrCreate()

    dbname = "tripdata"
    tblname = "ny_taxi" if len(sys.argv) <= 1 else sys.argv[1]
    bucket_name = "emr-local-dev" if len(sys.argv) <= 2 else sys.argv[2]
    dest_path = f"s3://{bucket_name}/{tblname}/"
    src_path = "s3://aws-data-analytics-workshops/shared_datasets/tripdata/"
    # read csv
    ny_taxi = spark.read.option("inferSchema", "true").option("header", "true").csv(src_path)
    ny_taxi = to_timestamp_df(ny_taxi, ["lpep_pickup_datetime", "lpep_dropoff_datetime"])
    ny_taxi.printSchema()
    # write parquet
    ny_taxi.write.mode("overwrite").parquet(dest_path)
    # create glue table
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
