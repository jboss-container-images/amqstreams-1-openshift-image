#!/bin/bash

set -e

SOURCES_DIR=/tmp/artifacts
SCRIPT_DIR=$(dirname $0)
SCRIPTS_DIR=${SCRIPT_DIR}/scripts
LICENSE_DIR=/root/licenses
PRODUCT_LICENSE_DIR=${LICENSE_DIR}/${COM_REDHAT_COMPONENT}

mkdir ${PRODUCT_LICENSE_DIR}
tar -xvzf ${LICENSE_DIR}/*.tgz -C ${PRODUCT_LICENSE_DIR}

mkdir $KAFKA_HOME
cp "${SOURCES_DIR}"/*.jar  ${KAFKA_HOME}

# copy scripts for starting Kafka Init
cp -r ${SCRIPTS_DIR}/* ${KAFKA_HOME}/

chown -R jboss:root ${KAFKA_HOME}
chmod -R 755 ${KAFKA_HOME}
