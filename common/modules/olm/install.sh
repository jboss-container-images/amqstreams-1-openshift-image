#!/bin/bash
set -e

SCRIPT_DIR=$(dirname $0)
MANIFESTS_DIR=${SCRIPT_DIR}/manifests

# create destination folder of manifests
mkdir -p /manifests

# copy manifests files
cp -r ${MANIFESTS_DIR}/* /manifests
