#!/usr/bin/env python3
"""########################################################
 FILE: backport_install.py
########################################################"""
import datetime
import re
import shutil
import os
from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import DoubleQuotedScalarString

from automation.modules import versions

yaml = YAML()
yaml.preserve_quotes = True
yaml.indent(mapping=2, sequence=4, offset=2)


def get_current_kafka_version():
    kafka_version = versions.get_kafka_version_to_replace(versions.get_product_version(versions.get_branch_name()))
    return f"{kafka_version}.0"


def get_target_kafka_version():
    kafka_version = versions.get_kafka_version_replacement(versions.get_product_version(versions.get_branch_name()))
    return f"{kafka_version}.0"


def get_current_kafka_registry_version():
    kafka_registry_version = versions.get_kafka_version_to_replace(versions.get_product_version(versions.get_branch_name()))
    kafka_registry_version = str(kafka_registry_version)[:-2].replace(".", "")
    return kafka_registry_version


def get_target_kafka_registry_version():
    kafka_registry_version = versions.get_kafka_version_replacement(versions.get_product_version(versions.get_branch_name()))
    kafka_registry_version = str(kafka_registry_version)[:-2].replace(".", "")
    return kafka_registry_version


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


def update_cluster_operator_deployment(file_path, release_version):
    with open(file_path, "r") as file:
        yaml_data = yaml.load(file)

    stripped_version = ".".join(release_version.split(".")[:2])
    common_fields = get_common_fields(yaml_data)

    # Update component version and YQ version
    common_fields["labels_field"]["rht.prod_ver"] = common_fields["target_release_quarter"]
    common_fields["labels_field"]["rht.comp_ver"] = stripped_version

    # Update container image version
    yaml_data["spec"]["template"]["spec"]["containers"][0]["image"] = \
        common_fields["common_registry_url"] + f"strimzi-rhel8-operator:{release_version}"

    # Update value: registry.redhat.io/amq-streams/kafka-<version>-rhel8:<version>
    update_streams_target_kafka_version = common_fields["common_registry_url"] + f"kafka-37-rhel8:{release_version}"
    for i in range(3, min(6, len(common_fields["env_field"]))):
        common_fields["env_field"][i]["value"] = update_streams_target_kafka_version

    #  Update Kafka upgrade and target image
    update_default_upgrade_kafka_image = f"{common_fields['current_kafka_version']}={common_fields['common_registry_url']}kafka-{common_fields['current_kafka_registry_version']}-rhel8:{release_version}"
    update_default_target_kafka_image = f"{common_fields['target_kafka_version']}={common_fields['common_registry_url']}kafka-{common_fields['target_kafka_registry_version']}-rhel8:{release_version}"
    for i in range(6, min(10, len(common_fields["env_field"]))):
        common_fields["env_field"][i][
            "value"] = f"{update_default_upgrade_kafka_image}\n{update_default_target_kafka_image}"
    # remove the added - at the end of the value, added by yaml parsing
    for item in common_fields["env_field"]:
        if "value" in item:
            item["value"] = item["value"].rstrip("|- \n") + "\n"

    # Update value; registry.redhat.io/amq-streams/strimzi-rhel8-operator:<version>
    update_strimzi_rhel8_operator = common_fields["common_registry_url"] + f"strimzi-rhel8-operator:{release_version}"
    for i in range(10, min(13, len(common_fields["env_field"]))):
        common_fields["env_field"][i]["value"] = update_strimzi_rhel8_operator

    # Update value; registry.redhat.io/amq-streams/bridge-rhel8:<version>
    update_bridge_rhel8 = common_fields["common_registry_url"] + f"bridge-rhel8:{release_version}"
    common_fields["env_field"][13]["value"] = update_bridge_rhel8

    # Update custom labels for year and quarter and version
    for i in range(23, 33):
        if common_fields["current_release_quarter"] in common_fields["env_field"][i]["value"]:
            common_fields["env_field"][i]["value"] = common_fields["env_field"][i]["value"].replace(
                common_fields["current_release_quarter"], common_fields["target_release_quarter"])

        if "2." in common_fields["env_field"][i]["value"]:
            common_fields["env_field"][i]["value"] = re.sub(r'2\.\d+', stripped_version,
                                                            common_fields["env_field"][i]["value"])

    with open(file_path, 'w') as file:
        yaml.dump(yaml_data, file)


def update_deployment_common(file_path, release_version, registry):
    with open(file_path, "r") as file:
        yaml_data = yaml.load(file)

    common_fields = get_common_fields(yaml_data)
    stripped_version = ".".join(release_version.split(".")[:2])  # remove the 0 to get 2.x
    common_fields["labels_field"]["rht.prod_ver"] = common_fields["target_release_quarter"]
    common_fields["labels_field"]["rht.comp_ver"] = DoubleQuotedScalarString(stripped_version)
    yaml_data["spec"]["template"]["spec"]["containers"][0]["image"] = registry + release_version

    with open(file_path, 'w') as file:
        yaml.dump(yaml_data, file)


registry_1 = "registry.redhat.io/amq-streams/drain-cleaner-rhel8:"
registry_2 = "registry.redhat.io/amq-streams/strimzi-rhel8-operator:"


def update_drain_cleaner_deployment(file_path, release_version):
    update_deployment_common(file_path, release_version, registry_1)


def update_user_deployment(file_path, release_version):
    update_deployment_common(file_path, release_version, registry_2)


def update_topic_deployment(file_path, release_version):
    update_deployment_common(file_path, release_version, registry_2)


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
