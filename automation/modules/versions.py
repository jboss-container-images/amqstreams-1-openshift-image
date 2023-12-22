#!/usr/bin/env python3
"""########################################################
 FILE: versions.py
########################################################"""
import re
import subprocess


def get_branch_name():
    return subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], capture_output=True,
                          text=True).stdout.strip()


def get_product_version(branch_name):
    number_pattern = r'\d+'
    numbers_in_branch = [int(match) for match in re.findall(number_pattern, branch_name)]
    return numbers_in_branch[0]


# Determine target Strimzi release number based on product version (which we extract from branch name)
def get_target_strimzi_version(product_version):
    strimzi_minor_version = 2 * (product_version - 26) + 38
    strimzi_version = f"0.{strimzi_minor_version}.0"
    return strimzi_version


# Determine latest Kafka release number based on product version (which we extract from branch name)
def get_latest_kafka_version(product_version):
    strimzi_minor_version = (product_version + 10)
    strimzi_version = f"{strimzi_minor_version / 10}"
    return strimzi_version


# Determine target Kafka Version
def get_target_kafka_version(product_version):
    result = float(get_latest_kafka_version(product_version)) + 0.1
    print("target Kafka version:" + str(result))
    return result
