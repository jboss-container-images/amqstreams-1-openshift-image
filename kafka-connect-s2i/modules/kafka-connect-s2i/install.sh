#!/bin/bash

set -e

SCRIPT_DIR=$(dirname $0)
ADDED_DIR=${SCRIPT_DIR}/added
SCRIPTS_DIR=${ADDED_DIR}/scripts

mkdir $S2I_HOME
cp -r ${SCRIPTS_DIR}/* ${S2I_HOME}/
chmod -R 755 ${S2I_HOME}
