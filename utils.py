import shutil
from pathlib import Path
from typing import List, Union
from pyspark.sql import DataFrame
from pyspark.sql.functions import col, to_timestamp


def to_timestamp_df(
    df: DataFrame, fields: Union[List[str], str], format: str = "M/d/yy H:mm"
) -> DataFrame:
    fields = [fields] if isinstance(fields, str) else fields
    for field in fields:
        df = df.withColumn(field, to_timestamp(col(field), format))
    return df


def remove_checkpoint():
    checkpoint_path = Path.joinpath(Path(__file__).parent.resolve(), ".checkpoint")
    print(f"remove checkpoint path - {checkpoint_path}")
    shutil.rmtree(checkpoint_path, ignore_errors=True)
