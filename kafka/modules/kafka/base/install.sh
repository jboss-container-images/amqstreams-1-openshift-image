#!/bin/bash

set -e

SOURCES_DIR=/tmp/artifacts
SCRIPT_DIR=$(dirname $0)
SCRIPTS_DIR=${SCRIPT_DIR}/scripts
STUNNEL_DIR=${SCRIPT_DIR}/stunnel-scripts
S2I_DIR=${SCRIPT_DIR}/s2i-scripts
EXPORTER_DIR=${SCRIPT_DIR}/exporter-scripts

mkdir $KAFKA_HOME
mkdir $STUNNEL_HOME
mkdir $S2I_HOME
mkdir $KAFKA_EXPORTER_HOME
mkdir -p -m g+rw /usr/local/var/run/

unzip -qo ${SOURCES_DIR}/kafka_exporter.zip -d ${KAFKA_EXPORTER_HOME}/

chmod -R 0755 ${KAFKA_HOME}

cp -r ${SCRIPTS_DIR}/* ${KAFKA_HOME}/
chmod -R 755 ${KAFKA_HOME}

cp -r ${STUNNEL_DIR}/* ${STUNNEL_HOME}/
chmod -R 755 ${STUNNEL_HOME}

cp -r ${S2I_DIR}/* ${S2I_HOME}/
chmod -R 755 ${S2I_HOME}

cp -r ${EXPORTER_DIR}/* ${KAFKA_EXPORTER_HOME}/
chmod -R 755 ${KAFKA_EXPORTER_HOME}
