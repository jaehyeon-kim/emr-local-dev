import shutil
import io
import json
import csv
from pathlib import Path
import boto3

BUCKET_NAME = "aws-data-analytics-workshops"
KEY_NAME = "shared_datasets/tripdata/tripdata.csv"
DATA_PATH = Path.joinpath(Path(__file__).parent, "json")


def recreate_data_path_if(data_path: Path, recreate: bool = True):
    if recreate:
        shutil.rmtree(data_path, ignore_errors=True)
        data_path.mkdir()


def write_to_json(bucket_name: str, key_name: str, data_path: Path, recreate: bool = True):
    s3 = boto3.resource("s3")
    data = io.BytesIO()
    bucket = s3.Bucket(bucket_name)
    bucket.download_fileobj(key_name, data)
    contents = data.getvalue().decode("utf-8")
    print("download complete")
    reader = csv.DictReader(contents.split("\n"))
    recreate_data_path_if(data_path, recreate)
    for c, row in enumerate(reader):
        record_id = str(c).zfill(5)
        data_path.joinpath(f"{record_id}.json").write_text(
            json.dumps({**{"record_id": record_id}, **row})
        )


if __name__ == "__main__":
    write_to_json(BUCKET_NAME, KEY_NAME, DATA_PATH, True)
