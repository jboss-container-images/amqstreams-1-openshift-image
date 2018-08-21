#!/bin/bash

set -e

SCRIPT_DIR=$(dirname $0)
ADDED_DIR=${SCRIPT_DIR}/added
CONFIG_DIR=${ADDED_DIR}/config
SCRIPTS_DIR=${ADDED_DIR}/scripts

# copy configuration files
cp -r ${CONFIG_DIR}/* ${KAFKA_HOME}/config/

# copy scripts for starting Zookeeper
cp -r ${SCRIPTS_DIR}/* ${KAFKA_HOME}/
chmod -R 755 ${KAFKA_HOME}
