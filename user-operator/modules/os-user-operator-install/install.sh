#!/bin/bash

set -e

SOURCES_DIR=/tmp/artifacts
SCRIPT_DIR=$(dirname $0)
ADDED_DIR=${SCRIPT_DIR}/added
SCRIPTS_DIR=${ADDED_DIR}/scripts

mkdir $AMQSTREAMS_HOME

chown -R jboss:root ${AMQSTREAMS_HOME}
chmod 0755 ${AMQSTREAMS_HOME}
chmod -R g+rwX ${AMQSTREAMS_HOME}

cp "${SOURCES_DIR}"/*.jar ${AMQSTREAMS_HOME}/

# copy scripts for starting User Operator
cp -r ${SCRIPTS_DIR}/* ${AMQSTREAMS_HOME}/
