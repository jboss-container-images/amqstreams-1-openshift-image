#!/usr/bin/env python3
"""########################################################
 FILE: main.py
########################################################"""
import os
from modules import backport
from modules import versions


def main():
    target_product_version = versions.get_product_version(versions.get_branch_name())
    target_strimzi_version = versions.get_target_strimzi_version(target_product_version)
    latest_kafka_version = versions.get_latest_kafka_version(target_product_version)
    target_kafka_version = versions.get_target_kafka_version(target_product_version)
    directory_path1 = ("strimzi-" + target_strimzi_version + "/examples")
    directory_path2 = "../examples"
    file_path1 = os.path.join("strimzi-" + target_strimzi_version,
                              "examples/security/keycloak-authorization/README.md")
    file_path2 = os.path.join("strimzi-" + target_strimzi_version,
                              "examples/connect/kafka-connect-build.yaml")
    strimzi_dir = "strimzi-" + target_strimzi_version

    versions.get_target_kafka_version(target_product_version)
    versions.get_target_strimzi_version(target_product_version)
    versions.get_latest_kafka_version(target_product_version)
    backport.create_release_url_for_zips(target_strimzi_version)
    backport.unpack_zips(target_strimzi_version)
    backport.compare_directory_files(directory_path1, directory_path2)
    backport.replace_version_in_files("strimzi-" + target_strimzi_version + "/examples", (".yaml", ".yml", ".json"),
                                      latest_kafka_version, target_kafka_version, "kafka")
    backport.replace_version_in_files("strimzi-" + target_strimzi_version + "/examples", (".yaml", ".yml", ".json"),
                                      latest_kafka_version, target_kafka_version, "inter_broker_protocol")
    backport.delete_excluded_directory('canary', 'install', strimzi_dir)  # Part of install refactor
    backport.delete_file(file_path1, file_path2)
    backport.string_replacement('strimzi-' + target_strimzi_version + '/examples', 'README.md')
    backport.copy_directory("examples", "examples", strimzi_dir)
    backport.copy_directory("install", "install", strimzi_dir)
    backport.delete_created_upstream_resources(strimzi_dir)


if __name__ == "__main__":
    main()
