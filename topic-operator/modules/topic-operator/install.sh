#!/bin/bash

set -e

SOURCES_DIR=/tmp/artifacts
SCRIPT_DIR=$(dirname $0)
SCRIPTS_DIR=${SCRIPT_DIR}/scripts
LICENSE_DIR=/root/licenses
PRODUCT_LICENSE_DIR=${LICENSE_DIR}/${COM_REDHAT_COMPONENT}

mkdir -p ${PRODUCT_LICENSE_DIR}
tar -xvzf ${LICENSE_DIR}/*.tgz -C ${PRODUCT_LICENSE_DIR}

cp -r ${SCRIPTS_DIR}/* /bin/
chmod -R 755 /bin/

mv "${SOURCES_DIR}/topic-operator.jar" /
