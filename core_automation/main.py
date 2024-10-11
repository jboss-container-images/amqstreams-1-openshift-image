#!/usr/bin/env python3
"""########################################################
 FILE: main.py
########################################################"""
import os
from modules import backport_examples, backport_install, versions

def get_paths(target_strimzi_version):
    """Helper function to build commonly used paths."""
    base_dir = f"strimzi-{target_strimzi_version}"
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return {
        'example_dir': os.path.join(base_dir, "examples"),
        'full_example_dir': f"{base_dir}/examples",
        'base_dir': base_dir,
        'full_base_dir': os.path.join(current_dir, base_dir),
        'example_dir_to_compare': "../examples"
    }

def get_file_and_directory_deletions(target_strimzi_version):
    """Helper function to return files and directories that need to be deleted."""
    base_dir = f"strimzi-{target_strimzi_version}"

    files = [
        os.path.join(base_dir, "examples/security/keycloak-authorization/README.md"),
        os.path.join(base_dir, "examples/connect/kafka-connect-build.yaml"),
        os.path.join(base_dir, "examples/kafka/kafka-with-node-pools.yaml"),
        os.path.join(base_dir, "CHANGELOG.md"),
    ]

    directories = [
        os.path.join(base_dir, "docs"),
        os.path.join(base_dir, "install/drain-cleaner/certmanager"),
        os.path.join(base_dir, "install/drain-cleaner/kubernetes"),
    ]

    return files, directories

def backport_example_files(target_strimzi_version, kafka_version_to_replace, kafka_version_replacement):
    """Helper function to handle all backport example operations."""
    paths = get_paths(target_strimzi_version)

    backport_examples.create_release_url_for_zips(target_strimzi_version)
    backport_examples.unpack_zips(target_strimzi_version)
    backport_examples.compare_directory_files(paths['example_dir'], paths['example_dir_to_compare'])
    backport_examples.update_yaml_files(paths['full_example_dir'], kafka_version_to_replace, kafka_version_replacement)

    files, directories = get_file_and_directory_deletions(target_strimzi_version)

    backport_examples.delete_file(*files)
    backport_examples.update_example_dir_readme(paths['full_example_dir'], 'README.md')
    backport_examples.copy_directory_excluding_readme("examples", "examples", paths['base_dir'])

def backport_install_files(target_strimzi_version, target_release_version):
    """Helper function to handle all backport installation operations."""
    paths = get_paths(target_strimzi_version)

    file_paths = [
        "/install/cluster-operator/060-Deployment-strimzi-cluster-operator.yaml",
        "/install/drain-cleaner/openshift/060-Deployment.yaml",
        "/install/topic-operator/05-Deployment-strimzi-topic-operator.yaml",
        "/install/user-operator/05-Deployment-strimzi-user-operator.yaml"
    ]

    files, directories = get_file_and_directory_deletions(target_strimzi_version)

    backport_install.delete_directory(*directories)
    backport_install.update_cluster_operator_deployment(f"{paths['full_base_dir']}/{file_paths[0]}", target_release_version)

    # Update deployments
    deployments = [
        (file_paths[1], "drain-cleaner", "application"),
        (file_paths[2], "topic-operator", "infrastructure"),
        (file_paths[3], "user-operator", "infrastructure")
    ]
    for file_path, component, kind in deployments:
        backport_install.update_deployment(f"{paths['full_base_dir']}{file_path}", target_release_version, component, kind)

    backport_install.delete_excluded_directory('canary', 'install', paths['base_dir'])
    backport_install.copy_directory("install", "install", paths['base_dir'])

def main():
    """Main entry point"""
    target_product_version = versions.get_product_version(versions.get_branch_name())
    target_strimzi_version = versions.get_target_strimzi_version(target_product_version)
    target_release_version = versions.get_target_micro_release_version()

    kafka_version_to_replace = versions.get_kafka_version_to_replace(target_product_version)
    kafka_version_replacement = versions.get_kafka_version_replacement(target_product_version)

    backport_example_files(target_strimzi_version, kafka_version_to_replace, kafka_version_replacement)
    backport_install_files(target_strimzi_version, target_release_version)

    # Clean up created upstream resources
    strimzi_dir = f"strimzi-{target_strimzi_version}"
    backport_examples.delete_created_upstream_resources(strimzi_dir)


if __name__ == "__main__":
    main()
