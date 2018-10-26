#!/bin/bash

set -e

SCRIPT_DIR=$(dirname $0)
SCRIPTS_DIR=${SCRIPT_DIR}/scripts

cp -r ${SCRIPTS_DIR}/* ${STUNNEL_HOME}/
chmod -R 755 ${STUNNEL_HOME}
