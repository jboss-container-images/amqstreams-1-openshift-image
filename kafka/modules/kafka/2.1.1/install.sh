#!/bin/bash

set -e

SOURCES_DIR=/tmp/artifacts
LICENSE_DIR=/root/licenses
PRODUCT_LICENSE_DIR=${LICENSE_DIR}/${COM_REDHAT_COMPONENT}

tar xvfz "${SOURCES_DIR}/kafka.tar.gz" -C ${KAFKA_HOME} --strip-components=1

mkdir -p ${PRODUCT_LICENSE_DIR}
cp ${KAFKA_HOME}/docs/licen*/* ${PRODUCT_LICENSE_DIR}
