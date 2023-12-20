#!/usr/bin/env python3
from modules import backport
from modules import versions
from modules.backport import file_path1, file_path2, directory_path1, directory_path2


def main():
    latest_strimzi_version = versions.get_latest_strimzi_release()
    latest_kafka_version = versions.get_latest_kafka_release()
    target_kafka_version = versions.get_target_kafka_version()
    versions.get_target_kafka_version()
    versions.get_latest_strimzi_release()
    versions.get_latest_kafka_release()
    backport.create_release_url_for_zips()
    backport.unpack_zips()
    backport.compare_directory_files(directory_path1, directory_path2)
    backport.replace_version_in_files("strimzi-" + latest_strimzi_version + "/examples", (".yaml", ".yml", ".json"),
                                      latest_kafka_version, target_kafka_version,  "kafka")
    backport.replace_version_in_files("strimzi-" + latest_strimzi_version + "/examples", (".yaml", ".yml", ".json"),
                                      latest_kafka_version, target_kafka_version, "inter_broker_protocol")
    backport.delete_excluded_directory('canary', 'install') # Part of install refactor
    backport.delete_file(file_path1, file_path2)
    backport.string_replacement('strimzi-' + latest_strimzi_version + '/examples', 'README.md')
    backport.copy_directory("examples", "examples")
    backport.copy_directory("install", "install")
    backport.delete_created_upstream_resources()


if __name__ == "__main__":
    main()
