#!/usr/bin/env python3
"""########################################################
 FILE: bundle_automation.py
########################################################"""
import yaml
import os
import re
import json
from . import constants


class BundleAutomation:

    @staticmethod
    def get_product_version(csv_data):
        data = yaml.safe_load(csv_data)
        return data['spec']['version'].split("-")[0]

    @staticmethod
    def get_replace_version(csv_data):
        data = yaml.safe_load(csv_data)
        return data['spec']['replaces'].split(".v")[-1]

    @staticmethod
    def get_bundle_version(csv_data):
        data = yaml.safe_load(csv_data)
        return data['spec']['version']

    @staticmethod
    def get_bundle_name(csv_data):
        data = yaml.safe_load(csv_data)
        return data['metadata']['name']

    @staticmethod
    def get_bundle_deployment_name(csv_data):
        data = yaml.safe_load(csv_data)
        return data['spec']['install']['spec']['deployments'][0]['name']

    @staticmethod
    def get_skip_range(csv_data):
        data = yaml.safe_load(csv_data)
        return data['metadata']['annotations']['olm.skipRange']

    @staticmethod
    def extract_version(name):
        return name.split("v")[-1]

    @staticmethod
    def is_build_released(brew_client, build):
        tags = brew_client.listTags(build)
        for tag in tags:
            if tag['name'] == constants.RELEASE_TAG:
                return True
        return False

    @staticmethod
    def decrement_minor_version(semver):
        semver_split = semver.split(".")
        semver_split[1] = str(int(semver_split[1]) - 1)
        return ".".join(semver_split)

    @staticmethod
    def increment_build_version(semver):
        semver_split = semver.split("-")
        semver_split[-1] = str(int(semver_split[-1]) + 1)
        return "-".join(semver_split)

    @staticmethod
    def set_build_version(semver, build_version):
        major_minor_micro = semver.split("-")[0]
        return major_minor_micro + "-" + str(build_version)

    @staticmethod
    def is_bundle_released(brew_client, product_version):
        # Sort to get latest build for version
        builds = brew_client.listBuilds(prefix=constants.METADATA_PACKAGE_NAME, queryOpts={'order': 'creation_ts'})
        # Reverse so latest build appear first
        builds.reverse()

        for build in builds:
            # Since the builds are in order take the latest build which matches the major and minor version
            if build['version'] == product_version:
                if BundleAutomation.is_build_released(brew_client, build):
                    return True
        return False

    """
    Gets nvr of latest brew build with the specified prefix e.g. amqstreams-operator-container-1.4.0-5
    """
    @staticmethod
    def get_nvr(brew_client, prefix, version):
        # Sort to get latest build for version
        builds = brew_client.listBuilds(prefix=prefix, queryOpts={'order': 'creation_ts'})
        # Reverse so latest build appear first
        builds.reverse()

        for build in builds:
            if build['version'] == version and build['state'] == constants.COMPLETED and "source" not in build['nvr']:
                if "openjdk-" in prefix:
                    if BundleAutomation.is_build_released(brew_client, build):
                        return build['nvr']
                else:
                    print(build['nvr'])
                    return build['nvr']

        raise ValueError('No NVR found in brew with prefix %s and version %s' % (prefix, version))

    @staticmethod
    def get_pull_spec_from_info(info):
        data = yaml.safe_load(info)
        return data["extra"]["image"]["index"]["digests"]["application/vnd.docker.distribution.manifest.list.v2+json"]

    @staticmethod
    def get_pull_spec_from_brew(brew_client, nvr):
        pull_spec = None
        try:
            # Get Manifest List Digest associated with nvr
            pull_spec = brew_client.getBuild(nvr)['extra']['image']['index']['digests'][
                'application/vnd.docker.distribution.manifest.list.v2+json']

            # Get Image Digest associated with nvr
            # sha = brew_client.listArchives(brew_client.getBuild(nvr)
            # ['build_id'])[0]['extra']['docker']['digests']['application/vnd.docker.distribution.manifest.v2+json']

            print("NVR:", nvr)
        except Exception as e:
            print(f"An unexpected error occurred: {e}. No NVR found in brew with value", nvr)

        return pull_spec

    @staticmethod
    def format_sha(s):
        return s.split(":")[-1]

    @staticmethod
    def get_start_interval(v):
        # Convert version to int
        v = int(v.split("-")[0].replace(".", ""))
        n = int((v - 10) / 10)
        n = ".".join(list(str(n) + "0")) + "-0"
        return n

    ''' 
    Parses build information stored in ENV VARs from builds executed in earlier stage in pipeline:
    
    'CONTAINER_BUILDS_OPERATOR_BUILD_INFO_JSON'
    'CONTAINER_BUILDS_BRIDGE_BUILD_INFO_JSON'
    'CONTAINER_BUILDS_DRAIN_CLEANER_BUILD_INFO_JSON'
    'CONTAINER_BUILDS_KAFKA_34_BUILD_INFO_JSON'
    'CONTAINER_BUILDS_KAFKA_35_BUILD_INFO_JSON'
  
    and returns a list of dictionaries in the following format:
  
    {
      'amqstreams-operator-container': '{BUILD_INFO_JSON}'
      'amqstreams-bridge-container': '{BUILD_INFO_JSON}'
      'amqstreams-drain-cleaner-container': '{BUILD_INFO_JSON}'
      'amqstreams-kafka-34-container': '{BUILD_INFO_JSON}'
      'amqstreams-kafka-35-container': '{BUILD_INFO_JSON}'
    }
    '''
    @staticmethod
    def collect_component_build_info():
        print(" ===== COLLECTING COMPONENT BUILD INFO ===== ")
        components = {}

        for k, v in os.environ.items():
            if k.startswith("CONTAINER_BUILDS") and k.endswith("BUILD_INFO_JSON"):
                info = json.loads(v)
                components[info["package_name"]] = v

        return components

    @staticmethod
    def get_maven_builder_pull_spec(brew_client, csv_data):
        product_version = BundleAutomation.get_bundle_version(csv_data).split("-")[0]

        if int(product_version.split(".")[0]) <= 2 and int(product_version.split(".")[1]) < 2:
            package_name = "openjdk-11-ubi8"
            version = "1.10"
        elif int(product_version.split(".")[0]) <= 2 and int(product_version.split(".")[1]) < 5:
            package_name = "openjdk-11-ubi8"
            version = "1.13"
        else:
            package_name = "openjdk-17-ubi8"
            version = "1.16"

        pull_spec = BundleAutomation.get_pull_spec_from_brew(
            brew_client,
            BundleAutomation.get_nvr(brew_client, package_name, version)
        )
        return pull_spec

    @staticmethod
    def generate_package_name(related_images_name):
        if related_images_name == "strimzi-cluster-operator":
            return constants.OPERATOR_PACKAGE_NAME
        elif related_images_name == "strimzi-maven-builder":
            return constants.STRIMZI_MAVEN_BUILDER + constants.PACKAGE_NAME_SUFFIX
        else:
            package_name = related_images_name.replace("strimzi", "amqstreams")
            # If Kafka image name e.g. strimzi-kafka-340
            # format version in generated nvr name
            if "kafka" in package_name:
                sep = package_name.split("-")
                # e.g. strimzi-kafka-340 -> strimzi-kafka-34
                sep[-1] = sep[-1][:2]
                package_name = "-".join(sep)

            package_name = package_name + constants.PACKAGE_NAME_SUFFIX
            return package_name

    @staticmethod
    def create_sha_dict(brew_client, csv_data, components):
        sha_dict = {}
        print("--- Replacing SHAs with latest NVRs ---")

        csv_data_yaml = yaml.safe_load(csv_data)
        for entry in csv_data_yaml["spec"]["relatedImages"]:
            name = entry['name']
            image = entry['image']

            package_name = BundleAutomation.generate_package_name(name)
            if name == constants.STRIMZI_MAVEN_BUILDER:
                pull_spec = BundleAutomation.get_maven_builder_pull_spec(brew_client, csv_data)
            else:
                pull_spec = BundleAutomation.get_pull_spec_from_info(components.get(package_name))

            old_sha = BundleAutomation.format_sha(image)
            new_sha = BundleAutomation.format_sha(pull_spec)

            print("OLD:", old_sha)
            print("NEW:", new_sha)
            print("")
            sha_dict[old_sha] = new_sha

        return sha_dict

    '''
    Returns list with the bundle version to be replaced 
    and the current bundle version respectively
  
    e.g. [2.5.0-0, 2.5.0-1]
    '''
    @staticmethod
    def generate_bundle_version_strings(brew_client, csv_data, new_pull_specs_exist):
        old_bundle_version = BundleAutomation.get_replace_version(csv_data)
        new_bundle_version = BundleAutomation.get_bundle_version(csv_data)

        released = BundleAutomation.is_bundle_released(brew_client, new_bundle_version.split("-")[0])
        if released and new_pull_specs_exist:
            old_bundle_version = new_bundle_version
            new_bundle_version = BundleAutomation.increment_build_version(new_bundle_version)

        print("Updating " + old_bundle_version + " -> " + new_bundle_version)

        return [old_bundle_version, new_bundle_version]

    @staticmethod
    def new_pull_specs_exist(sha_dict):
        for k, v in sha_dict.items():
            if k != v:
                return True
        return False

    @staticmethod
    def update_csv_data(csv_data, bundle_versions, sha_dict):
        old_bundle_version = bundle_versions[0]
        new_bundle_version = bundle_versions[1]

        for old_sha, new_sha in sha_dict.items():
            csv_data = csv_data.replace(old_sha, new_sha)

        csv_data = csv_data.replace(old_bundle_version, new_bundle_version)

        start_interval = BundleAutomation.get_start_interval(new_bundle_version)
        csv_data = re.sub(r"olm.skipRange: '>=\d.\d.\d-\d <\d.\d.\d-\d'",
                          "olm.skipRange: '>=" + start_interval + " <" + new_bundle_version + "'", csv_data)
        csv_data = re.sub(r'replaces: amqstreams.v.*..*..*', 'replaces: amqstreams.v' + old_bundle_version, csv_data)

        return csv_data
