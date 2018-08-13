#!/bin/bash

set -e

SOURCES_DIR=/tmp/artifacts
SCRIPT_DIR=$(dirname $0)
ADDED_DIR=${SCRIPT_DIR}/added
SCRIPTS_DIR=${ADDED_DIR}/scripts

mkdir $KAFKA_HOME
#tar xvfz "${SOURCES_DIR}/*.tar.gz" -C ${KAFKA_HOME} --strip-components=1
cp "${SOURCES_DIR}"/*.jar  ${KAFKA_HOME}

chown -R jboss:root ${KAFKA_HOME}
chmod 0755 ${KAFKA_HOME}
chmod -R g+rwX ${KAFKA_HOME}

# copy scripts for starting Kafka Connect
cp -r ${SCRIPTS_DIR}/* ${KAFKA_HOME}/
