#!/bin/bash

set -e

SCRIPT_DIR=$(dirname $0)
ADDED_DIR=${SCRIPT_DIR}/added
CONFIG_DIR=${ADDED_DIR}/config
SCRIPTS_DIR=${ADDED_DIR}/scripts

# copy configs for Kafka Connect
cp -r ${CONFIG_DIR}/* ${KAFKA_HOME}/config/

# copy scripts for starting Kafka Connect
cp -r ${SCRIPTS_DIR}/* ${KAFKA_HOME}/