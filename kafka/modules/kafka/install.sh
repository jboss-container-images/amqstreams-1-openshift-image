#!/bin/bash

set -e

SCRIPT_DIR=$(dirname $0)
CONFIG_DIR=${SCRIPT_DIR}/config
SCRIPTS_DIR=${SCRIPT_DIR}/scripts

cp -r ${CONFIG_DIR}/* ${KAFKA_HOME}/config/

cp -r ${SCRIPTS_DIR}/* ${KAFKA_HOME}/
