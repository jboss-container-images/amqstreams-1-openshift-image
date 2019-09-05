#!/bin/bash

set -e

SOURCES_DIR=/tmp/artifacts
SCRIPT_DIR=$(dirname $0)
SCRIPTS_DIR=${SCRIPT_DIR}/scripts
STUNNEL_DIR=${SCRIPT_DIR}/stunnel-scripts
S2I_DIR=${SCRIPT_DIR}/s2i-scripts

mkdir -p $KAFKA_HOME/libs/
mkdir $STUNNEL_HOME
mkdir $S2I_HOME
mkdir -p -m g+rw /usr/local/var/run/

mkdir /opt/prometheus
mkdir /opt/prometheus/config
cp -r ${SOURCES_DIR}/jmx_prometheus_javaagent.jar /opt/prometheus/jmx_prometheus_javaagent.jar
cp -r ${SOURCES_DIR}/kafka-agent.jar ${KAFKA_HOME}/libs/

chmod -R 0755 ${KAFKA_HOME}
chmod -R 0755 /opt/prometheus

cp -r ${SCRIPTS_DIR}/* ${KAFKA_HOME}/
chmod -R 755 ${KAFKA_HOME}

cp -r ${STUNNEL_DIR}/* ${STUNNEL_HOME}/
chmod -R 755 ${STUNNEL_HOME}

cp -r ${S2I_DIR}/* ${S2I_HOME}/
chmod -R 755 ${S2I_HOME}
