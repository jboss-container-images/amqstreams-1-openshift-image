#!/bin/bash
set -e

SCRIPT_DIR=$(dirname $0)
MANIFESTS_DIR=${SCRIPT_DIR}/manifests

# create destination folder of manifests
mkdir -p ${STRIMZI_HOME}/manifests

# copy manifests files
cp -r ${MANIFESTS_DIR}/* ${STRIMZI_HOME}/manifests

chmod -R 0755 ${STRIMZI_HOME}/manifests