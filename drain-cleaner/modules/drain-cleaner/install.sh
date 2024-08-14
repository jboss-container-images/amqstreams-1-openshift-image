#!/bin/bash
set -e

SOURCES_DIR=/tmp/artifacts
LICENSE_DIR=/root/licenses
PRODUCT_LICENSE_DIR=${LICENSE_DIR}/${COM_REDHAT_COMPONENT}

# Add strimzi user with UID 1001
useradd -r -m -u 1001 -g 0 strimzi

# untar the artifact containing license information
mkdir -p ${PRODUCT_LICENSE_DIR}
mv ${SOURCES_DIR}/drain-cleaner-licenses.tar.gz ${LICENSE_DIR}
tar -xvzf ${LICENSE_DIR}/drain-cleaner-licenses.tar.gz -C ${PRODUCT_LICENSE_DIR} --no-same-owner

mkdir -p ${STRIMZI_HOME}

# copy jar and execution script
cp ${SOURCES_DIR}/drain-cleaner.jar ${STRIMZI_HOME}
cp ${SCRIPT_DIR}/drain_cleaner_run.sh ${STRIMZI_HOME}/bin

chmod -R 0755 ${STRIMZI_HOME}/
chmod -R 0755 ${STRIMZI_HOME}/bin
