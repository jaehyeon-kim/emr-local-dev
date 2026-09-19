# Spark Local Development Environment Using Docker

A local development environment for Apache Spark applications that are meant to run on Amazon EMR. The Docker image is built from the EMR 6.5.0 Spark image that AWS publishes to ECR, so the Spark version, the class path and the Glue Data Catalog integration match the cluster. VS Code opens the repository inside that container through the Dev Containers extension, and a small Kafka stack runs alongside it for the streaming example. Four example scripts at the repository root cover spark-submit, pytest, a Jupyter notebook and Spark Structured Streaming.

## Posts

- [Develop and Test Apache Spark Apps for EMR Locally Using Docker](https://jaehyeon.me/blog/2022-05-08-emr-local-dev/). It links `.devcontainer/Dockerfile`, `.devcontainer/spark/spark-defaults.conf` and `.devcontainer/spark/log4j.properties`.
- Originally published at [cevo.com.au](https://cevo.com.au/post/develop-and-test-apache-spark-apps-for-emr-locally-using-docker/).

## Examples

Each script runs inside the development container, from `/home/hadoop/repo`.

| File | What it demonstrates | How to run it |
|---|---|---|
| [tripdata.py](tripdata.py) | spark-submit with Glue Data Catalog integration. It reads the public New York taxi CSV files from `s3://aws-data-analytics-workshops/shared_datasets/tripdata/`, converts two columns to timestamps with `to_timestamp_df` from [utils.py](utils.py), writes Parquet to S3, and creates the Glue database `tripdata` and a table over that location. The table name and bucket name are the first and second arguments, defaulting to `ny_taxi` and `emr-local-dev`. | `$SPARK_HOME/bin/spark-submit --deploy-mode client --master local[*] tripdata.py` |
| [test_utils.py](test_utils.py) | pytest against a local Spark session. Two cases check that `to_timestamp_df` parses a timestamp with the right format and raises `Py4JError` with the wrong one. It touches no AWS service. | `pytest -v` |
| [tripdata.ipynb](tripdata.ipynb) | A Jupyter notebook in VS Code. It loads credentials from a `.env` file with `python-dotenv`, queries the Glue table `tripdata.ny_taxi` that `tripdata.py` created, and summarises trip duration, distance and amount. Run `tripdata.py` first, because the notebook reads its output. | Open the file in VS Code and run the cells. |
| [tripdata_notify.py](tripdata_notify.py) | Spark Structured Streaming writing to Kafka. It reads the JSON files in `data/json` as a stream, keeps the rows whose `total_amount` is negative, and writes them to the `notifications` topic on `kafka:9092`. Run `python data/generate.py` first: that script downloads `tripdata.csv` and writes one JSON file per row into `data/json`. The topic can then be inspected in Kafka UI on port 8080. | `$SPARK_HOME/bin/spark-submit --deploy-mode client --master local[*] --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.2 tripdata_notify.py` |

## Environment

[.devcontainer](.devcontainer) holds the whole environment.

- `Dockerfile` builds on `038297999601.dkr.ecr.ap-southeast-2.amazonaws.com/spark/emr-6.5.0:20211119`. It gives the `hadoop` user sudo, copies `spark/spark-defaults.conf` and `spark/log4j.properties` into the Spark configuration folder, and installs the Python packages in `pkgs/requirements.txt`. Build it with `docker build -t=emr-6.5.0:20211119 .devcontainer/`.
- `spark/spark-defaults.conf` sets `spark.hadoop.hive.metastore.client.factory.class` to `AWSGlueDataCatalogHiveClientFactory`, which is what makes the Glue Data Catalog act as the metastore. It also sets `spark.hadoop.fs.s3.customAWSCredentialsProvider` to `EnvironmentVariableCredentialsProvider`, so Spark reads AWS credentials from environment variables rather than from a profile.
- `docker-compose.yml` defines seven services. `devcontainer.json` starts four of them: `spark`, `zookeeper` (`bitnami/zookeeper:3.7.0`), `kafka` (`bitnami/kafka:2.8.1`) and `kafka-ui` (`provectuslabs/kafka-ui:0.3.3`). The other three, `kafka-connect`, `postgres` and `registry`, are left out of `runServices` and are not started. `connect/download-connectors.sh` downloads the Debezium PostgreSQL 1.8.1, Confluent S3 10.0.5 and Voluble 0.3.1 plugins that the `kafka-connect` service would mount.
- `devcontainer.json` mounts the repository at `/home/hadoop/repo`, forwards port 4040 for the Spark UI, and sets `PYTHONPATH` to the bundled `pyspark` and `py4j` packages of the Spark distribution.

## What you need before building

The README used to leave these out, and each of them stops the environment from working.

- An AWS profile that can pull from ECR in `ap-southeast-2`. The base image is an EMR on EKS release image held in the ECR registry of the AWS account `038297999601`, and that registry needs a login, so `docker build` fails at the `FROM` line without one. Authenticate first with `aws ecr get-login-password --region ap-southeast-2 | docker login --username AWS --password-stdin 038297999601.dkr.ecr.ap-southeast-2.amazonaws.com`. The account id differs by region, so a different region needs a different id and a rewritten `FROM` line.
- S3 and Glue permissions for `tripdata.py`: read on `s3://aws-data-analytics-workshops`, read and write on the destination bucket, and `glue:CreateDatabase`, `glue:CreateTable` and the matching get actions. `data/generate.py` needs the same read permission on the source bucket. The notebook needs read access to the destination bucket and the Glue table. Only `test_utils.py` runs without AWS credentials.
- Credentials in two forms. The Spark examples read `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION` and, when a role is assumed, `AWS_SESSION_TOKEN` from the environment, because of the `EnvironmentVariableCredentialsProvider` setting above. `data/generate.py` uses boto3, which reads `AWS_PROFILE` and `~/.aws` instead.
- `devcontainer.json` sets `AWS_PROFILE` to `cevo`. That profile name comes from the original author's machine and will not exist on yours, so change it to one of your own profiles or remove the entry. The `spark` service in `docker-compose.yml` mounts your `~/.aws` into the container at `/home/hadoop/.aws`, which is where that profile is looked up.

## Docker images

Bitnami's public Docker images have been moved to the [**Bitnami Legacy**](https://hub.docker.com/u/bitnamilegacy) repository. To ensure continued access and compatibility, please update your Docker image references accordingly.

For example:

- `bitnami/zookeeper:3.7.0` → `bitnamilegacy/zookeeper:3.7.0`
- `bitnami/kafka:2.8.1` → `bitnamilegacy/kafka:2.8.1`

Both tags appear in `.devcontainer/docker-compose.yml`.

## License

MIT. See [LICENSE](LICENSE).
