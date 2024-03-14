#!/usr/bin/env python3
"""########################################################
 FILE: main.py
########################################################"""
import os
from modules import backport_examples
from modules import backport_install
from modules import versions

def main():
    target_product_version = versions.get_product_version(versions.get_branch_name())
    target_strimzi_version = versions.get_target_strimzi_version(target_product_version)
    kafka_version_to_replace = versions.get_kafka_version_to_replace(target_product_version)
    kafka_version_replacement = versions.get_kafka_version_replacement(target_product_version)
    target_example_dir_path = ("strimzi-" + target_strimzi_version + "/examples")
    target_example_dir_path2 = "../examples"
    example_files_to_delete = [
        os.path.join("strimzi-" + target_strimzi_version, "examples/security/keycloak-authorization/README.md"),
        os.path.join("strimzi-" + target_strimzi_version, "examples/connect/kafka-connect-build.yaml"),
    ]
    strimzi_dir = "strimzi-" + target_strimzi_version

    backport_examples.create_release_url_for_zips(target_strimzi_version)
    backport_examples.unpack_zips(target_strimzi_version)
    backport_examples.compare_directory_files(target_example_dir_path, target_example_dir_path2)
    backport_examples.update_yaml_files("strimzi-" + target_strimzi_version + "/examples", kafka_version_to_replace,
                                        kafka_version_replacement)
    backport_examples.delete_file(*example_files_to_delete)
    backport_examples.update_example_dir_readme('strimzi-' + target_strimzi_version + '/examples', 'README.md')
    backport_examples.copy_directory("examples", "examples", strimzi_dir)
    backport_examples.delete_created_upstream_resources(strimzi_dir)

    # -------------------------------------------------------------------------------------------------------------#

    # Backport Install Files
    target_release_version = versions.get_target_release_version("2.7.0")
    file_paths = [
        "../install/cluster-operator/060-Deployment-strimzi-cluster-operator.yaml",
        "../install/drain-cleaner/openshift/060-Deployment.yaml",
        "../install/topic-operator/05-Deployment-strimzi-topic-operator.yaml",
        "../install/user-operator/05-Deployment-strimzi-user-operator.yaml"
    ]
    backport_install.delete_excluded_directory('canary', 'install', strimzi_dir)  # Part of install refactor
    backport_install.update_cluster_operator_deployment(file_paths[0], target_release_version)
    backport_install.update_drain_cleaner_deployment(file_paths[1], target_release_version)
    backport_install.update_topic_deployment(file_paths[2], target_release_version)
    backport_install.update_user_deployment(file_paths[3], target_release_version)


if __name__ == "__main__":
    main()
