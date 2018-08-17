#!/bin/bash

set -e

SCRIPT_DIR=$(dirname $0)
ADDED_DIR=${SCRIPT_DIR}/added
SCRIPTS_DIR=${ADDED_DIR}/scripts

# copy scripts for starting Kafka
cp -r ${SCRIPTS_DIR}/* ${KAFKA_HOME}/
