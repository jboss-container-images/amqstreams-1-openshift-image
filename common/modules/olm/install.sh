#!/bin/bash
set -e

SCRIPT_DIR=$(dirname $0)
MANIFESTS_DIR=${SCRIPT_DIR}/manifests

# create destination folder of manifests
mkdir -p /manifests
# create destination folder of metadata
mkdir -p /metadata

# copy manifests files
cp -r ${MANIFESTS_DIR}/*.yaml /manifests
# copy metadata file
cp -r ${MANIFESTS_DIR}/metadata/* /metadata
