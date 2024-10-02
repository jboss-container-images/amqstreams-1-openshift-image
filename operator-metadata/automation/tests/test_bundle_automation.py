import os
import unittest

from automation.modules import constants
from automation.modules.file import File
from automation.modules.bundle_automation import BundleAutomation


class TestBundleAutomation(unittest.TestCase):
    RESOURCES_PATH = "resources/"
    DESCRIPTOR_FILE_PATH = RESOURCES_PATH + "test.image.yaml"
    OLD_CSV_FILE_PATH = RESOURCES_PATH + "old.format.test.bundle.clusterserviceversion.yaml"
    NEW_CSV_FILE_PATH = RESOURCES_PATH + "new.format.test.bundle.clusterserviceversion.yaml"

    OPERATOR_PULL_SPEC_REPLACEMENT = "test0"
    KAFKA_PREVIOUS_PULL_SPEC_REPLACEMENT = "test1"
    KAFKA_CURRENT_PULL_SPEC_REPLACEMENT = "test2"
    BRIDGE_PULL_SPEC_REPLACEMENT = "test3"
    MAVEN_PULL_SPEC_REPLACEMENT = "test4"

    def setUp(self):
        build_info = [
            "CONTAINER_BUILDS_BRIDGE_BUILD_INFO_JSON",
            "CONTAINER_BUILDS_DRAIN_CLEANER_BUILD_INFO_JSON",
            "CONTAINER_BUILDS_KAFKA_34_BUILD_INFO_JSON",
            "CONTAINER_BUILDS_KAFKA_35_BUILD_INFO_JSON",
            "CONTAINER_BUILDS_OPERATOR_BUILD_INFO_JSON"
        ]

        for component in build_info:
            with open(self.RESOURCES_PATH + component, 'r') as file:
                data = file.read().rstrip()
                os.environ[component] = data

        self.descriptor = File(TestBundleAutomation.DESCRIPTOR_FILE_PATH)
        self.csv = File(TestBundleAutomation.OLD_CSV_FILE_PATH)

    def test_collect_component_build_info(self):
        build_info = BundleAutomation.collect_component_build_info()
        self.assertEqual(len(build_info), 5)

    def test_generate_package_name_from_annotation(self):
        operator_annotation = {"operator-image": "registry.redhat.io/amq-streams/strimzi-rhel9-operator@sha256:95f5aa75cd1f7228e78fd4d88d786713fba4cf828dc22bc2dd1d0380909c1aef"}
        kafka_prev_annotation = {"kafka-previous-image": "registry.redhat.io/amq-streams/kafka-36-rhel9@sha256:177484ebf6f663eedfc558285e4e89e817277389250aec29323452082b6949e4"}
        kafka_curr_annotation = {"kafka-current-image": "registry.redhat.io/amq-streams/kafka-37-rhel9@sha256:42bf60ce31540dd61fab2c9886d791e41f063ea6f86628694b9e60e49bc8951b"}
        bridge_annotation = {"bridge-image": "registry.redhat.io/amq-streams/bridge-rhel9@sha256:4db7b231d68a244f5f71c8587123890e1344be933e1a030097c4b32a9bbfe32d"}
        maven_annotation =  {"maven-image":  "registry.redhat.io/amq-streams/maven-builder-rhel9@sha256:2393070a07677a482e90f53fef58f12e1c73963cf164738aaa1c095e5fe77d0d"}
        non_image_annotation = {"test": "test"}

        self.assertEqual(BundleAutomation.generate_package_name_from_annotation(operator_annotation), "amqstreams-operator-container")
        self.assertEqual(BundleAutomation.generate_package_name_from_annotation(kafka_prev_annotation), "amqstreams-kafka-36-container")
        self.assertEqual(BundleAutomation.generate_package_name_from_annotation(kafka_curr_annotation), "amqstreams-kafka-37-container")
        self.assertEqual(BundleAutomation.generate_package_name_from_annotation(bridge_annotation), "amqstreams-bridge-container")
        self.assertEqual(BundleAutomation.generate_package_name_from_annotation(maven_annotation), "amqstreams-maven-builder-container")
        self.assertEqual(BundleAutomation.generate_package_name_from_annotation(non_image_annotation), None)

    def test_update_old_csv_format(self):
        self._test_update_csv_file(
            csv_file_path=self.OLD_CSV_FILE_PATH,
            bundle_versions=["2.5.0-0", "2.5.0-1"],
            replacement_map={
                "3eec64199147feed58986202781dec4bf3efa43e7585aa37012c265af16a95c4": self.OPERATOR_PULL_SPEC_REPLACEMENT,
                "385d66c176995111ae06a875e6849dcb3c70db68a305bcb029759208d0c7c9ef": self.KAFKA_PREVIOUS_PULL_SPEC_REPLACEMENT,
                "9f43707f3b6b893177cb50fe77b92a742c90b48f39c77d4a8f4ebe340634a46b": self.KAFKA_CURRENT_PULL_SPEC_REPLACEMENT,
                "e534a7105a2eeb7c11f4d604987a70459f84561dfa9bcb59173630fc21b5c58c": self.BRIDGE_PULL_SPEC_REPLACEMENT,
                "8796da64c626c5f63f31a4e3ac0ac3b179333a7c6d5472a195b9b3f61ccd1099": self.MAVEN_PULL_SPEC_REPLACEMENT
            },
            sha_count={
                self.OPERATOR_PULL_SPEC_REPLACEMENT: 6,
                self.KAFKA_PREVIOUS_PULL_SPEC_REPLACEMENT: 5,
                self.KAFKA_CURRENT_PULL_SPEC_REPLACEMENT: 8,
                self.BRIDGE_PULL_SPEC_REPLACEMENT: 2,
                self.MAVEN_PULL_SPEC_REPLACEMENT: 2
            },
            expected_related_images=True
        )

    def test_update_new_csv_format(self):
        self._test_update_csv_file(
            csv_file_path=self.NEW_CSV_FILE_PATH,
            bundle_versions=["2.7.0-0", "2.7.0-1"],
            replacement_map={
                "strimzi-rhel9-operator:2.7.0-14": self.OPERATOR_PULL_SPEC_REPLACEMENT,
                "kafka-36-rhel9:2.7.0-18": self.KAFKA_PREVIOUS_PULL_SPEC_REPLACEMENT,
                "kafka-37-rhel9:2.7.0-13": self.KAFKA_CURRENT_PULL_SPEC_REPLACEMENT,
                "bridge-rhel9:2.7.0-14": self.BRIDGE_PULL_SPEC_REPLACEMENT,
                "maven-builder-rhel9:2.7.0-11": self.MAVEN_PULL_SPEC_REPLACEMENT
            },
            sha_count={
                self.OPERATOR_PULL_SPEC_REPLACEMENT: 3,
                self.KAFKA_PREVIOUS_PULL_SPEC_REPLACEMENT: 2,
                self.KAFKA_CURRENT_PULL_SPEC_REPLACEMENT: 2,
                self.BRIDGE_PULL_SPEC_REPLACEMENT: 1,
                self.MAVEN_PULL_SPEC_REPLACEMENT: 1
            },
            expected_related_images=False
        )

    def _test_update_csv_file(self, csv_file_path, bundle_versions, replacement_map, sha_count, expected_related_images):
        automation = BundleAutomation()
        cluster_service_version_file = File(csv_file_path)

        # Update CSV with new version numbers and SHA hashes or tags
        data = automation.update_cluster_service_version_data(cluster_service_version_file.data, bundle_versions, replacement_map)

        # Check replaces field
        self.assertEqual(bundle_versions[constants.OLD_BUNDLE_VERSION_INDEX], automation.get_replace_version(data))

        # Check version fields
        bundle_version = bundle_versions[constants.NEW_BUNDLE_VERSION_INDEX]
        self.assertEqual(bundle_version, automation.get_bundle_version(data))
        self.assertEqual(bundle_version, automation.extract_version(automation.get_bundle_name(data)))
        self.assertEqual(bundle_version, automation.extract_version(automation.get_bundle_deployment_name(data)))

        # Check skipRange field
        bundle_version_start = automation.set_build_version(automation.decrement_minor_version(bundle_version), 0)
        self.assertEqual(bundle_version_start, automation.get_skip_range(data).split("<")[0].split("=")[-1].strip())
        self.assertEqual(bundle_version, automation.get_skip_range(data).split("<")[-1])

        # Check pull_spec replacement counts
        for old_pull_spec, new_pull_spec in replacement_map.items():
            self.assertEqual(data.count(new_pull_spec), sha_count[new_pull_spec])

        # Check relatedImages field
        self.assertEqual("relatedImages" in cluster_service_version_file.data, expected_related_images)

if __name__ == "__main__":
    unittest.main()
