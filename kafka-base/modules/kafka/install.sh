#!/bin/bash

set -e

SOURCES_DIR=/tmp/artifacts

mkdir $KAFKA_HOME
tar xvfz "${SOURCES_DIR}/kafka.tar.gz" -C ${KAFKA_HOME} --strip-components=1

mkdir /opt/prometheus
mkdir /opt/prometheus/config
mv ${SOURCES_DIR}/jmx_prometheus_javaagent.jar /opt/prometheus/jmx_prometheus_javaagent.jar

chown -R jboss:root ${KAFKA_HOME}/bin
chmod 0755 ${KAFKA_HOME}/bin