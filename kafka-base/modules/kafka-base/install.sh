#!/bin/bash

set -e

SOURCES_DIR=/tmp/artifacts
SCRIPT_DIR=$(dirname $0)
SCRIPTS_DIR=${SCRIPT_DIR}/scripts

mkdir $KAFKA_HOME
tar xvfz "${SOURCES_DIR}/kafka.tar.gz" -C ${KAFKA_HOME} --strip-components=1

mkdir /opt/prometheus
mkdir /opt/prometheus/config
mv ${SOURCES_DIR}/jmx_prometheus_javaagent.jar /opt/prometheus/jmx_prometheus_javaagent.jar

chown -R jboss:root ${KAFKA_HOME}
chmod -R 0755 ${KAFKA_HOME}
chown -R jboss:root /opt/prometheus
chmod -R 0755 /opt/prometheus

cp -r ${SCRIPTS_DIR}/* ${KAFKA_HOME}/
chmod -R 755 ${KAFKA_HOME}
