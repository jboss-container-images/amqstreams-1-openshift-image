#!/usr/bin/env python3
"""########################################################
 FILE: versions.py
########################################################"""
import re
import subprocess


# Determine latest Strimzi release number using git branch
def get_latest_strimzi_release():
    current_branch = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], capture_output=True,
                                    text=True).stdout.strip()
    number_pattern = r'\d+'
    numbers_in_branch = [int(match) for match in re.findall(number_pattern, current_branch)]
    upstream = numbers_in_branch[0]
    result = 2 * (upstream - 26) + 38
    downstream = f"0.{result}.0"
    return downstream


# Determine latest Kafka release using git branch
def get_latest_kafka_release():
    current_branch = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], capture_output=True,
                                    text=True).stdout.strip()
    number_pattern = r'\d+'
    numbers_in_branch = [int(match) for match in re.findall(number_pattern, current_branch)]
    upstream = numbers_in_branch[0]
    result = (upstream + 10)
    downstream = f"{result / 10}"
    return downstream


# Determine target Kafka Version
def get_target_kafka_version():
    result = float(get_latest_kafka_release()) + 0.1
    print("target Kafka version:" + str(result))
    return result
