#!/bin/bash

set -e

SCRIPT_DIR=$(dirname $0)
ADDED_DIR=${SCRIPT_DIR}/added
SCRIPTS_DIR=${ADDED_DIR}/scripts

cp -r ${SCRIPTS_DIR}/* ${STUNNEL_HOME}/
chmod -R 755 ${STUNNEL_HOME}
