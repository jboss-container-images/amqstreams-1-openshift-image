#!/bin/bash

set -e

SOURCES_DIR=/tmp/artifacts
LICENSE_DIR=/root/licenses
PRODUCT_LICENSE_DIR=${LICENSE_DIR}/${COM_REDHAT_COMPONENT}

# Copy contents of AMQ Streams/Kafka zip without the root dir
TMP=$(zipinfo -1  ${SOURCES_DIR}/streams-ocp-*.zip | grep -oE '^[^/]+' | uniq)
unzip ${SOURCES_DIR}/streams-ocp-*.zip
mv ${TMP}/* ${KAFKA_HOME}/

cp -r ${KAFKA_HOME}/bin/kafka_exporter ${KAFKA_EXPORTER_HOME}/

mkdir -p ${PRODUCT_LICENSE_DIR}
cp ${KAFKA_HOME}/docs/licen*/* ${PRODUCT_LICENSE_DIR}

# Copy contents of Cruise Control zip without the root dir
TMP=$(zipinfo -1  ${SOURCES_DIR}/cruise-control-ocp-*.zip | grep -oE '^[^/]+' | uniq)
unzip ${SOURCES_DIR}/cruise-control-ocp-*.zip
mv ${TMP}/* ${CRUISE_CONTROL_HOME}/libs/