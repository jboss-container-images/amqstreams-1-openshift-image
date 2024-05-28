#!/usr/bin/env python3
"""########################################################
 FILE: test_versions.py
########################################################"""
import unittest
from core_automation.modules import versions


class TestVersions(unittest.TestCase):

    def test_get_product_version(self):
        branch_name = "amqstreams26-dev"
        expected_product_version = 26
        actual_product_version = versions.get_product_version(branch_name)
        self.assertEqual(actual_product_version, expected_product_version)

        branch_name = "amqstreams27-dev"
        expected_product_version = 27
        actual_product_version = versions.get_product_version(branch_name)
        self.assertEqual(actual_product_version, expected_product_version)

    def test_get_target_strimzi_release(self):
        product_version = 26
        expected_strimzi_version = "0.38.0"
        actual_strimzi_version = versions.get_target_strimzi_version(product_version)
        self.assertEqual(actual_strimzi_version, expected_strimzi_version)

        product_version = 27
        expected_strimzi_version = "0.40.0"
        actual_strimzi_version = versions.get_target_strimzi_version(product_version)
        self.assertEqual(actual_strimzi_version, expected_strimzi_version)

    def test_get_latest_kafka_release(self):
        product_version = 26
        expected_kafka_version = "3.6"
        actual_kafka_version = versions.get_kafka_version_to_replace(product_version)
        self.assertEqual(actual_kafka_version, expected_kafka_version)

        product_version = 27
        expected_kafka_version = "3.7"
        actual_kafka_version = versions.get_kafka_version_to_replace(product_version)
        self.assertEqual(actual_kafka_version, expected_kafka_version)

    def test_get_target_kafka_version(self):
        product_version = 26
        expected_kafka_version = 3.7
        actual_kafka_version = versions.get_kafka_version_replacement(product_version)
        self.assertEqual(actual_kafka_version, expected_kafka_version)

        product_version = 27
        expected_kafka_version = 3.8
        actual_kafka_version = versions.get_kafka_version_replacement(product_version)
        self.assertEqual(actual_kafka_version, expected_kafka_version)


if __name__ == '__main__':
    unittest.main()
