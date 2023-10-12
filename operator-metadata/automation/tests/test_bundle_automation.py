import os
import unittest

from automation.modules import constants
from automation.modules.bundle_automation import BundleAutomation
from automation.modules.file import File


class TestBundleAutomation(unittest.TestCase):
    RESOURCES_PATH = "resources/"
    DESCRIPTOR_FILE_PATH = RESOURCES_PATH + "test.image.yaml"
    CSV_FILE_PATH = RESOURCES_PATH + "test.bundle.clusterserviceversion.yaml"

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
        self.csv = File(TestBundleAutomation.CSV_FILE_PATH)

    def test_collect_component_build_info(self):
        build_info = BundleAutomation.collect_component_build_info()
        self.assertEqual(len(build_info), 5)

    def test_update_csv_file(self):
        automation = BundleAutomation()

        csv_file = File(self.CSV_FILE_PATH)
        bundle_versions = ["2.5.0-0", "2.5.0-1"]

        operator_sha = "test0"
        kafka_35_sha = "test1"
        kafka_34_sha = "test2"
        bridge_sha = "test3"
        maven_builder_sha = "test4"

        sha_dict = {
            "3eec64199147feed58986202781dec4bf3efa43e7585aa37012c265af16a95c4": operator_sha,
            "9f43707f3b6b893177cb50fe77b92a742c90b48f39c77d4a8f4ebe340634a46b": kafka_35_sha,
            "385d66c176995111ae06a875e6849dcb3c70db68a305bcb029759208d0c7c9ef": kafka_34_sha,
            "e534a7105a2eeb7c11f4d604987a70459f84561dfa9bcb59173630fc21b5c58c": bridge_sha,
            "8796da64c626c5f63f31a4e3ac0ac3b179333a7c6d5472a195b9b3f61ccd1099": maven_builder_sha
                   }

        # Update CSV with new versions numbers and SHA hashes
        data = automation.update_csv_data(csv_file.data, bundle_versions, sha_dict)

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

        # Check SHA replacement
        self.assertEqual(6, data.count(operator_sha))
        self.assertEqual(8, data.count(kafka_35_sha))
        self.assertEqual(5, data.count(kafka_34_sha))
        self.assertEqual(2, data.count(bridge_sha))
        self.assertEqual(2, data.count(maven_builder_sha))


if __name__ == "__main__":
    unittest.main()
