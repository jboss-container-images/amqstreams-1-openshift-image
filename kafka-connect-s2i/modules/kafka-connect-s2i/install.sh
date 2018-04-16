#!/bin/bash

set -e

SCRIPT_DIR=$(dirname $0)
SCRIPTS_DIR=${SCRIPT_DIR}/scripts

mkdir $S2I_HOME
cp -r ${SCRIPTS_DIR}/* ${S2I_HOME}/