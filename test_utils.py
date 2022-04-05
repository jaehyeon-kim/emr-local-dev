import pytest
import datetime
from pyspark.sql import SparkSession
from py4j.protocol import Py4JError

from utils import to_timestamp_df


@pytest.fixture(scope="session")
def spark():
    return (
        SparkSession.builder.master("local")
        .appName("test")
        .config("spark.submit.deployMode", "client")
        .getOrCreate()
    )


def test_to_timestamp_success(spark):
    raw_df = spark.createDataFrame(
        [("1/1/17 0:01",)],
        ["date"],
    )

    test_df = to_timestamp_df(raw_df, "date", "M/d/yy H:mm")
    for row in test_df.collect():
        assert row["date"] == datetime.datetime(2017, 1, 1, 0, 1)


def test_to_timestamp_bad_format(spark):
    raw_df = spark.createDataFrame(
        [("1/1/17 0:01",)],
        ["date"],
    )

    with pytest.raises(Py4JError):
        to_timestamp_df(raw_df, "date", "M/d/yy HH:mm").collect()
