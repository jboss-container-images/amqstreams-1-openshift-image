#!/bin/bash

set -e

SOURCES_DIR=/tmp/artifacts
SCRIPT_DIR=$(dirname $0)
ADDED_DIR=${SCRIPT_DIR}/added
SCRIPTS_DIR=${ADDED_DIR}/scripts

cp -r ${SCRIPTS_DIR}/* /bin/
chmod -R 755 /bin/

mv "${SOURCES_DIR}/topic-operator.jar" /
