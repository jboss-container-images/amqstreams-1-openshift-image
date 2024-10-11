#!/usr/bin/env python3
"""########################################################
 FILE: versions.py
########################################################"""
import re
import git

# Determine current branch name from active repo
def get_branch_name():
    repo = git.Repo(search_parent_directories=True)
    return repo.active_branch.name


# Determine product version based on branch name
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
def get_kafka_version_to_replace(product_version):
    strimzi_minor_version = (product_version + 10)
    strimzi_version = f"{strimzi_minor_version / 10}"
    return strimzi_version


# Determine target Kafka Version
def get_kafka_version_replacement(product_version):
    result = round(float(get_kafka_version_to_replace(product_version)) + 0.1, 1)
    print("target Kafka version:" + str(result))
    return result


# Determine target Streams Version
def get_target_streams_minor_version():
    kafka_version = str(get_kafka_version_replacement(get_product_version(get_branch_name())))
    kafka_version = "2" + kafka_version[1:]  # Replace the first digit with 2
    return kafka_version


def get_target_micro_release_version():
    release_version = get_target_streams_minor_version()
    if not release_version.endswith(".0"):
        release_version += ".0"  # Add .0 if it's not already there
    return release_version
