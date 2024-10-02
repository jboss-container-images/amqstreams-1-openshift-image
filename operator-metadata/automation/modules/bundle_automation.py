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

    STRIMZI_DEPLOYMENT=0

    @staticmethod
    def get_product_version(data):
        data = yaml.safe_load(data)
        return data['spec']['version'].split("-")[0]

    @staticmethod
    def get_replace_version(data):
        data = yaml.safe_load(data)
        return data['spec']['replaces'].split(".v")[-1]

    @staticmethod
    def get_bundle_version(data):
        data = yaml.safe_load(data)
        return data['spec']['version']

    @staticmethod
    def get_bundle_name(data):
        data = yaml.safe_load(data)
        return data['metadata']['name']

    @staticmethod
    def get_bundle_deployment_name(data):
        data = yaml.safe_load(data)
        return data['spec']['install']['spec']['deployments'][BundleAutomation.STRIMZI_DEPLOYMENT]['name']

    @staticmethod
    def get_skip_range(data):
        data = yaml.safe_load(data)
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
                return build['nvr']

        raise ValueError('No NVR found in brew with prefix %s and version %s' % (prefix, version))

    @staticmethod
    def get_digest_from_info(info):
        data = yaml.safe_load(info)
        return data["extra"]["image"]["index"]["digests"]["application/vnd.docker.distribution.manifest.list.v2+json"]

    def get_pull_spec_from_info(info):
        data = yaml.safe_load(info)
        pull_spec_with_tag=1
        pull_spec = data["extra"]["image"]["index"]["pull"][pull_spec_with_tag]
        return pull_spec

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
    def generate_package_name(related_images_name):
        if related_images_name == "strimzi-cluster-operator":
            return constants.OPERATOR_PACKAGE_NAME
        elif related_images_name == "strimzi-maven-builder":
            return constants.MAVEN_BUILDER_PACKAGE_NAME
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
    def generate_package_name_from_annotation(annotation):
        package_mapping = {
          "operator-image" : "amqstreams-operator-container",
          "bridge-image"   : "amqstreams-bridge-container",
          "maven-image" : "amqstreams-maven-builder-container"
        }
        key = next(iter(annotation))
        val = annotation.get(key)
        if key in package_mapping:
            return package_mapping.get(key)
        if "previous" or "current" in key:
            match = re.search(r'kafka-(\d+)', val)
            if match:
              kafka_version = match.group(1)
              return "amqstreams-kafka-" + kafka_version + "-container"
            else:
              print("ERROR: Cannot extract Kafka version number from Kafka pull spec: " + val)
              return None
        else:
            return None

    @staticmethod
    def create_tag_dict_from_new_csv_format(brew_client, data, components):
        tag_dict = {}

        print("--- Replacing pull specs with latest NVRs ---")
        yaml_data = yaml.safe_load(data)
        try:
          annotations = yaml_data["spec"]["install"]["spec"]["deployments"][BundleAutomation.STRIMZI_DEPLOYMENT]["spec"]["template"]["metadata"]["annotations"]
        except KeyError as e:
          print(f"ERROR: pull spec replacement failed due to missing key {e} in Cluster Service Version file")
          annotations = {}

        for annotation in annotations:
            key = next(iter(annotation))
            pull_spec_from_annotations = annotation.get(key)
            package_name =  BundleAutomation.generate_package_name_from_annotation(annotation)
            if package_name:
              # CPaaS provides pull_specs in format: "<PLACEHOLDER>/rh-osbs/amq-streams-bridge-rhel8:2.5.0-5"
              pull_spec_from_build_info = BundleAutomation.get_pull_spec_from_info(components.get(package_name))

              # Because tags are not unique we use image name + tag
              # to know which pull specs to update in the cluster service version file
              old_image_name_and_tag = pull_spec_from_annotations.split("/")[-1]
              new_image_name_and_tag = pull_spec_from_build_info.split("amq-streams-")[1]

              print("OLD:", old_image_name_and_tag)
              print("NEW:", new_image_name_and_tag)
              print("")
              tag_dict[old_image_name_and_tag] = new_image_name_and_tag

        return tag_dict

    @staticmethod
    def create_sha_dict_from_old_csv_format(brew_client, data, components):
        sha_dict = {}
        print("--- Replacing SHAs with latest NVRs ---")

        data_yaml = yaml.safe_load(data)
        for entry in data_yaml["spec"]["relatedImages"]:
            name = entry['name']
            image = entry['image']

            package_name = BundleAutomation.generate_package_name(name)
            pull_spec = BundleAutomation.get_digest_from_info(components.get(package_name))

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
    def generate_bundle_version_strings(brew_client, data, product_version):
        # Sort to get latest build for version
        builds = brew_client.listBuilds(prefix=constants.METADATA_PACKAGE_NAME, queryOpts={'order': 'creation_ts'})
        # Reverse so latest build appear first
        builds.reverse()

        respin_number = 0;
        for build in builds:
        # Since the builds are in order take the latest build which matches the major and minor version
            if build['version'] == product_version:
                if BundleAutomation.is_build_released(brew_client, build):
                    respin_number+=1;

        old_bundle_version = BundleAutomation.get_replace_version(data)
        new_bundle_version = product_version + "-" + str(respin_number)

        if(respin_number > 0):
            old_bundle_version = product_version + "-" + str(respin_number-1)

        print("Updating " + old_bundle_version + " -> " + new_bundle_version)

        return [old_bundle_version, new_bundle_version]

    @staticmethod
    def new_pull_specs_exist(sha_dict):
        for k, v in sha_dict.items():
            if k != v:
                return True
        return False

    @staticmethod
    def update_cluster_service_version_data(data, bundle_versions, tag_dict):
        old_bundle_version = bundle_versions[0]
        new_bundle_version = bundle_versions[1]

        for old, new in tag_dict.items():
            data = data.replace(old, new)

        data = data.replace(old_bundle_version, new_bundle_version)

        start_interval = BundleAutomation.get_start_interval(new_bundle_version)
        data = re.sub(r"olm.skipRange: '>=\d.\d.\d-\d <\d.\d.\d-\d'",
                          "olm.skipRange: '>=" + start_interval + " <" + new_bundle_version + "'", data)
        data = re.sub(r'replaces: amqstreams.v.*..*..*', 'replaces: amqstreams.v' + old_bundle_version, data)

        return data
