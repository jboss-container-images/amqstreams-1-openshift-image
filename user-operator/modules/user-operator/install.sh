#!/bin/bash
set -e

SCRIPT_DIR=$(dirname $0)
SCRIPTS_DIR=${SCRIPT_DIR}/scripts
SOURCES_DIR=/tmp/artifacts
LICENSE_DIR=/root/licenses
PRODUCT_LICENSE_DIR=${LICENSE_DIR}/${COM_REDHAT_COMPONENT}

mkdir ${PRODUCT_LICENSE_DIR}
tar -xvzf ${LICENSE_DIR}/*.tgz -C ${PRODUCT_LICENSE_DIR}

chmod -R ug+x ${SCRIPTS_DIR}/*
mv ${SCRIPTS_DIR}/* /bin

chmod -R 0755 ${SOURCES_DIR}/*
mv ${SOURCES_DIR}/* /
