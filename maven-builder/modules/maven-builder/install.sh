#!/bin/bash
set -e

# Add strimzi user with UID 1001
# The user is in the group 0 to have access to the mounted volumes and storage
useradd -r -m -u 1001 -g 0 strimzi

# create destination folder of scripts, jars and config
mkdir -p ${STRIMZI_HOME}
