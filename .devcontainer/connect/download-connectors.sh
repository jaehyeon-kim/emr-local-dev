#!/usr/bin/env bash

echo "Add avro converter? (Y/N)"
read WITH_AVRO

SCRIPT_DIR="$(cd $(dirname "$0"); pwd)"

echo $SCRIPT_DIR

SRC_PATH=${SCRIPT_DIR}/src
rm -rf ${SCRIPT_DIR}/src && mkdir -p ${SRC_PATH}

## Debezium Source Connector
echo "downloading debezium postgres connector..."
DOWNLOAD_URL=https://repo1.maven.org/maven2/io/debezium/debezium-connector-postgres/1.8.1.Final/debezium-connector-postgres-1.8.1.Final-plugin.tar.gz

curl -S -L ${DOWNLOAD_URL} | tar -C ${SRC_PATH} --warning=no-unknown-keyword -xzf -

## Confluent S3 Sink Connector
echo "downloading confluent s3 connector..."
DOWNLOAD_URL=https://d1i4a15mxbxib1.cloudfront.net/api/plugins/confluentinc/kafka-connect-s3/versions/10.0.5/confluentinc-kafka-connect-s3-10.0.5.zip

curl ${DOWNLOAD_URL} -o ${SRC_PATH}/confluent.zip \
  && unzip -qq ${SRC_PATH}/confluent.zip -d ${SRC_PATH} \
  && rm ${SRC_PATH}/confluent.zip \
  && mv ${SRC_PATH}/$(ls ${SRC_PATH} | grep confluentinc-kafka-connect-s3) ${SRC_PATH}/confluent-s3

## Voluble Source Connector
echo "downloading voluble connector..."
DOWNLOAD_URL=https://d1i4a15mxbxib1.cloudfront.net/api/plugins/mdrogalis/voluble/versions/0.3.1/mdrogalis-voluble-0.3.1.zip

curl ${DOWNLOAD_URL} -o ${SRC_PATH}/voluble.zip \
  && unzip -qq ${SRC_PATH}/voluble.zip -d ${SRC_PATH} \
  && rm ${SRC_PATH}/voluble.zip \
  && mv ${SRC_PATH}/$(ls ${SRC_PATH} | grep mdrogalis-voluble) ${SRC_PATH}/voluble

if [ ${WITH_AVRO} == "Y" ]; then
  echo "downloading kafka connect avro converter..."
  DOWNLOAD_URL=https://d1i4a15mxbxib1.cloudfront.net/api/plugins/confluentinc/kafka-connect-avro-converter/versions/6.0.3/confluentinc-kafka-connect-avro-converter-6.0.3.zip

  curl ${DOWNLOAD_URL} -o ${SRC_PATH}/avro.zip \
    && unzip -qq ${SRC_PATH}/avro.zip -d ${SRC_PATH} \
    && rm ${SRC_PATH}/avro.zip \
    && mv ${SRC_PATH}/$(ls ${SRC_PATH} | grep confluentinc-kafka-connect-avro-converter) ${SRC_PATH}/avro

  echo "copying to connectors..."
  cp -r ${SRC_PATH}/avro/lib/* ${SRC_PATH}/debezium-connector-postgres
  cp -r ${SRC_PATH}/avro/lib/* ${SRC_PATH}/confluent-s3/lib
  cp -r ${SRC_PATH}/avro/lib/* ${SRC_PATH}/voluble/lib
fi