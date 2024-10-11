#!/usr/bin/env python3
"""########################################################
 FILE: backport_install.py
########################################################"""
import datetime
import shutil
import os

from ruamel import yaml
from ruamel.yaml import YAML
from core_automation.modules import versions


def represent_multiline_str(representer, data):
    if '\n' in data:
        return representer.represent_scalar(tag='tag:yaml.org,2002:str', value=data, style='|')
    return representer.represent_scalar(tag='tag:yaml.org,2002:str', value=data)


yaml = YAML()
yaml.preserve_quotes = True
yaml.representer.add_representer(str, represent_multiline_str)
yaml.indent(mapping=2, sequence=4, offset=2)


def get_common_fields(yaml_data):
    common_fields = {}
    common_fields["labels_field"] = yaml_data["spec"]["template"]["metadata"]["labels"]
    common_fields["env_field"] = yaml_data["spec"]["template"]["spec"]["containers"][0]["env"]
    common_fields["common_registry_url"] = "registry.redhat.io/amq-streams/"
    common_fields["current_year"], common_fields["current_quarter"] = get_current_year_and_quarter()
    last_year, last_quarter = get_last_year_and_quarter()  # Getting last year and quarter
    common_fields["last_year"] = last_year
    common_fields["last_quarter"] = last_quarter
    common_fields["current_kafka_version"] = get_current_kafka_version()
    common_fields["target_kafka_version"] = get_target_kafka_version()
    common_fields["current_kafka_registry_version"] = get_current_kafka_registry_version()
    common_fields["target_kafka_registry_version"] = get_target_kafka_registry_version()
    common_fields["current_release_quarter"] = str(last_year) + ".Q" + str(last_quarter)
    common_fields["target_release_quarter"] = str(common_fields["current_year"]) + ".Q" + str(
        common_fields["current_quarter"])
    return common_fields


def get_current_kafka_version():
    kafka_version = versions.get_kafka_version_to_replace(versions.get_product_version(versions.get_branch_name()))
    return f"{kafka_version}.0"


def get_target_kafka_version():
    kafka_version = versions.get_kafka_version_replacement(versions.get_product_version(versions.get_branch_name()))
    return f"{kafka_version}.0"


def get_current_kafka_registry_version():
    kafka_registry_version = versions.get_kafka_version_to_replace(
        versions.get_product_version(versions.get_branch_name()))
    kafka_registry_version = str(kafka_registry_version).replace(".", "")
    return kafka_registry_version


def get_target_kafka_registry_version():
    kafka_registry_version = versions.get_kafka_version_replacement(
        versions.get_product_version(versions.get_branch_name()))
    kafka_registry_version = str(kafka_registry_version).replace(".", "")
    return kafka_registry_version


def get_current_streams_version():
    streams_version = versions.get_target_streams_minor_version()
    return streams_version


def get_current_year_and_quarter():
    now = datetime.datetime.now()
    year = now.year
    month = now.month

    # Determine quarter based on month
    if month <= 3:
        quarter = 1
    elif month <= 6:
        quarter = 2
    elif month <= 9:
        quarter = 3
    else:
        quarter = 4
    return year, quarter


def get_last_year_and_quarter():
    current_year, current_quarter = get_current_year_and_quarter()

    if current_quarter == 1:
        last_year = current_year - 1
        last_quarter = 4
    else:
        last_year = current_year
        last_quarter = current_quarter - 1
    return last_year, last_quarter


def format_year_and_quarter():
    year, quarter = get_current_year_and_quarter()
    formatted_quarter = str(f"{year}.Q{quarter}")
    return formatted_quarter


def generate_env_var(name, subcomp, subcomp_t):
    env_common = {
        "com.company": "Red_Hat",
        "rht.prod_name": "Red_Hat_Application_Foundations",
        "rht.prod_ver": format_year_and_quarter(),
        "rht.comp": "AMQ_Streams",
        "rht.comp_ver": get_current_streams_version(),
        "rht.subcomp": subcomp,
        "rht.subcomp_t": subcomp_t
    }
    value = "\n".join(f"{key}={value}" for key, value in env_common.items())
    return {
        "name": name,
        "value": value
    }


def update_cluster_operator_deployment(file_path, release_version):
    with open(file_path, "r") as file:
        yaml_data = yaml.load(file)
    common_fields = get_common_fields(yaml_data)
    containers = yaml_data["spec"]["template"]["spec"]["containers"]
    env_vars = yaml_data["spec"]["template"]["spec"]["containers"][0]["env"]
    labels = yaml_data["spec"]["template"]["metadata"]["labels"]

    KAFKA_ENV_VARS_TO_UPDATE = ["STRIMZI_DEFAULT_TLS_SIDECAR_ENTITY_OPERATOR_IMAGE",
                                "STRIMZI_DEFAULT_KAFKA_EXPORTER_IMAGE",
                                "STRIMZI_DEFAULT_CRUISE_CONTROL_IMAGE"]
    STRIMZI_ENV_VARS_TO_UPDATE = ["STRIMZI_DEFAULT_TOPIC_OPERATOR_IMAGE",
                                  "STRIMZI_DEFAULT_USER_OPERATOR_IMAGE",
                                  "STRIMZI_DEFAULT_KAFKA_INIT_IMAGE"]
    KAFKA_MULTI_ENV_VARS_TO_UPDATE = ["STRIMZI_KAFKA_IMAGES",
                                      "STRIMZI_KAFKA_CONNECT_IMAGES",
                                      "STRIMZI_KAFKA_MIRROR_MAKER_IMAGES",
                                      "STRIMZI_KAFKA_MIRROR_MAKER_2_IMAGES"]
    BRIDGE_ENV_VARS_TO_UPDATE = "STRIMZI_DEFAULT_KAFKA_BRIDGE_IMAGE",
    MAVEN_ENV_VARS_TO_UPDATE = "STRIMZI_DEFAULT_MAVEN_BUILDER"
    KANIKO_ENV_VARS = "STRIMZI_DEFAULT_KANIKO_EXECUTOR_IMAGE"
    update_default_upgrade_kafka_image = f"{common_fields['current_kafka_version']}={common_fields['common_registry_url']}kafka-{common_fields['current_kafka_registry_version']}-rhel9:{release_version}"
    update_default_target_kafka_image = f"{common_fields['target_kafka_version']}={common_fields['common_registry_url']}kafka-{common_fields['target_kafka_registry_version']}-rhel9:{release_version}"

    new_env_var = {
        'name': 'STRIMZI_DEFAULT_TLS_SIDECAR_ENTITY_OPERATOR_IMAGE',
        'value': 'registry.redhat.io/amq-streams/kafka-37-rhel9:2.7.0'
    }

    # Insert the new environment variable after STRIMZI_OPERATION_TIMEOUT_MS
    updated_env_vars = []
    added = False
    for env_var in env_vars:
        updated_env_vars.append(env_var)
        if env_var['name'] == "STRIMZI_OPERATION_TIMEOUT_MS" and not added:
            updated_env_vars.append(new_env_var)
            added = True
    env_vars[:] = updated_env_vars

    label_env = {
        "strimzi.io/kind": "cluster-operator",
        "com.company": "Red_Hat",
        "rht.prod_name": "Red_Hat_Application_Foundations",
        "rht.prod_ver": format_year_and_quarter(),
        "rht.comp": "AMQ_Streams",
        "rht.comp_ver": get_current_streams_version(),
        "rht.subcomp": "cluster-operator",
        "rht.subcomp_t": "infrastructure"
    }

    labels.update(label_env)
    containers[0]['image'] = common_fields["common_registry_url"] + f"strimzi-rhel9-operator:{release_version}"
    kafka_version = get_target_kafka_registry_version()

    for env_var in env_vars:
        if env_var['name'] in KAFKA_ENV_VARS_TO_UPDATE:
            env_var['value'] = common_fields["common_registry_url"] + f"kafka-{kafka_version}-rhel9:{release_version}"
        if env_var['name'] in STRIMZI_ENV_VARS_TO_UPDATE:
            env_var['value'] = common_fields["common_registry_url"] + f"strimzi-rhel9-operator:{release_version}"
        if env_var['name'] in BRIDGE_ENV_VARS_TO_UPDATE:
            env_var['value'] = common_fields["common_registry_url"] + f"bridge-rhel9:{release_version}"
        if env_var['name'] in MAVEN_ENV_VARS_TO_UPDATE:
            env_var['value'] = "registry.redhat.io/ubi8/openjdk-17:1.16"
        # *********************************************************
        if env_var['name'] in KAFKA_MULTI_ENV_VARS_TO_UPDATE:
            env_var['value'] = f"{update_default_upgrade_kafka_image}\n{update_default_target_kafka_image}"

        # *********************************************************

    # I had to allow this its own loop because for some reason MAVEN_ENV_VARS_TO_UPDATE wouldn't update**********
    for kaniko in env_vars:
        if kaniko['name'] == KANIKO_ENV_VARS:
            env_vars.remove(kaniko)

    service_labels = {
        "discovery.3scale.net=true",
    }

    env_vars.append({
        "name": "STRIMZI_CUSTOM_KAFKA_BRIDGE_SERVICE_LABELS",
        "value": "\n".join(service_labels)})

    annotations = {
        "discovery.3scale.net/scheme=http",
        "discovery.3scale.net/port=8080",
        "discovery.3scale.net/path=/",
        "discovery.3scale.net/description-path=/openapi"
    }
    env_vars.append({
        "name": "STRIMZI_CUSTOM_KAFKA_BRIDGE_SERVICE_ANNOTATIONS",
        "value": "\n".join(annotations)})

    env_vars.append(generate_env_var("STRIMZI_CUSTOM_KAFKA_LABELS", "kafka-broker", "application"))
    env_vars.append(generate_env_var("STRIMZI_CUSTOM_KAFKA_CONNECT_LABELS", "kafka-connect", "application"))
    env_vars.append(
        generate_env_var("STRIMZI_CUSTOM_KAFKA_CONNECT_BUILD_LABELS", "kafka--connect-build", "application"))
    env_vars.append(generate_env_var("STRIMZI_CUSTOM_ZOOKEEPER_LABELS", "zookeeper", "infrastructure"))
    env_vars.append(generate_env_var("STRIMZI_CUSTOM_ENTITY_OPERATOR_LABELS", "entity-operator", "infrastructure"))
    env_vars.append(generate_env_var("STRIMZI_CUSTOM_KAFKA_MIRROR_MAKER2_LABELS", "kafka-mirror-maker2", "application"))
    env_vars.append(generate_env_var("STRIMZI_CUSTOM_KAFKA_MIRROR_MAKER_LABELS", "kafka-broker", "application"))
    env_vars.append(generate_env_var("TRIMZI_CUSTOM_CRUISE_CONTROL_LABELS", "cruise-control", "application"))
    env_vars.append(generate_env_var("STRIMZI_CUSTOM_KAFKA_BRIDGE_LABELS", "kafka-bridge", "application"))
    env_vars.append(generate_env_var("STRIMZI_CUSTOM_KAFKA_EXPORTER_LABELS", "afka-exporter", "application"))

    with open(file_path, 'w') as file:
        yaml.default_style = '|'
        yaml.dump(yaml_data, file)


def update_deployment(file_path, release_version, subcomp, subcomp_type):
    with open(file_path, "r") as file:
        yaml_data = yaml.load(file)
    common_fields = get_common_fields(yaml_data)
    containers = yaml_data["spec"]["template"]["spec"]["containers"]
    labels = yaml_data["spec"]["template"]["metadata"]["labels"]
    label_env = {
        "com.company": "Red_Hat",
        "rht.prod_name": "Red_Hat_Application_Foundations",
        "rht.prod_ver": format_year_and_quarter(),
        "rht.comp": "AMQ_Streams",
        "rht.comp_ver": get_current_streams_version(),
        "rht.subcomp": subcomp,
        "rht.subcomp_t": subcomp_type
    }
    labels.update(label_env)

    images = {
        "drain-cleaner": "drain-cleaner-rhel9",
        "topic-operator": "strimzi-rhel9-operator",
        "user-operator": "strimzi-rhel9-operator"
    }

    image_name = images.get(subcomp)
    if image_name:
        containers[0]['image'] = f"{common_fields['common_registry_url']}{image_name}:{release_version}"

    if subcomp == "drain-cleaner":
        containers[0].update({
            "command": [
                "/application",
                "-Dquarkus.http.host=0.0.0.0",
                "--kafka",
                "--zookeeper"
            ]
        })
    # Remove the args field
    if "args" in containers[0]:
        del containers[0]["args"]

    with open(file_path, 'w') as file:
        yaml.dump(yaml_data, file)


# copy upstream directory to downstream directory
def copy_directory(source_name, dest_name, strimzi_dir):
    source_dir = os.path.join(strimzi_dir, source_name)
    dest_dir = f'../{dest_name}'
    try:
        shutil.copytree(source_dir, dest_dir,
                        dirs_exist_ok=True)  # Copy the contents of the source directory to the destination
        print(f'{source_name} directory copied to {dest_name} successfully.')
    except Exception as e:
        print(f'Error copying {source_name} directory to {dest_name}:', e)


def delete_directory(*file_paths):
    for file_path in file_paths:
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f'Successfully deleted file: {file_path}')
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
                print(f'Successfully deleted directory and its contents: {file_path}')
            else:
                print(f'File or directory not found: {file_path}')
        except OSError as e:
            print(f'Error deleting file or directory {file_path}: {e}')


def delete_excluded_directory(folder_name, module_name, strimzi_dir):
    target_dir = os.path.join(strimzi_dir, module_name)
    delete_folder = os.path.join(target_dir, folder_name)
    try:
        shutil.rmtree(delete_folder)
        print(delete_folder + ' folder deleted successfully.')
    except FileNotFoundError:
        print('Target folder not found.')
    except Exception as e:
        print('Error deleting folder:', e)
