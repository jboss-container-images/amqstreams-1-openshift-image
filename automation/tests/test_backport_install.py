#!/usr/bin/env python3
"""########################################################
 FILE: test_backport_install.py
########################################################"""
import unittest
import yaml

from automation.modules.backport_install import (update_user_deployment, update_topic_deployment,
                                                 update_drain_cleaner_deployment,
                                                 update_cluster_operator_deployment,
                                                 get_current_year_and_quarter, get_last_year_and_quarter)

def _load_yaml_data(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

class TestBackportExampleAutomation(unittest.TestCase):
    RESOURCES_PATH = "resources/"
    COMMON_REGISTRY_URL = "registry.redhat.io/amq-streams/"
    EXPECTED_NEWEST_KAFKA_VERSION = "3.7.0"
    EXPECTED_UPGRADE_KAFKA_VERSION = "3.6.0"
    RHT_COMP_VERSION = "2.7"
    STRIMZI_VERSION = "2.7.0"
    YEAR_AND_QUARTER_VERSION = "2024.Q1"

    @classmethod
    def setUpClass(cls):
        cls.USER_OPERATOR_DEPLOYMENT_FILE = cls.RESOURCES_PATH + "test.05-Deployment-strimzi-user-operator.yaml"
        cls.TOPIC_OPERATOR_DEPLOYMENT_FILE = cls.RESOURCES_PATH + "test.05-Deployment-strimzi-topic-operator.yaml"
        cls.CLUSTER_OPERATOR_DEPLOYMENT_FILE = cls.RESOURCES_PATH + "test.060-Deployment-strimzi-cluster-operator.yaml"
        cls.DRAIN_CLEANER_OPENSHIFT_DEPLOYMENT_FILE = cls.RESOURCES_PATH + "test.060-Deployment-strimzi-drain-cleaner-openshift.yaml"

    def _assert_yaml_fields(self, yaml_data, expected_fields):
        image_field = yaml_data["spec"]["template"]["spec"]["containers"][0]["image"]
        label_field = yaml_data["spec"]["template"]["metadata"]["labels"]
        self.assertEqual(image_field, expected_fields)
        self.assertEqual(label_field["rht.comp_ver"], self.RHT_COMP_VERSION)
        self.assertEqual(label_field["rht.prod_ver"], self.YEAR_AND_QUARTER_VERSION)

    def test_yaml_parse(self):
        yaml_data = _load_yaml_data(self.USER_OPERATOR_DEPLOYMENT_FILE)
        expected_metadata = {'app': 'strimzi'}
        self.assertEqual(yaml_data["metadata"]["labels"], expected_metadata)

    def test_update_cluster_operator_deployment(self):
        update_cluster_operator_deployment(self.CLUSTER_OPERATOR_DEPLOYMENT_FILE, self.STRIMZI_VERSION)
        yaml_data = _load_yaml_data(self.CLUSTER_OPERATOR_DEPLOYMENT_FILE)
        env_field = yaml_data["spec"]["template"]["spec"]["containers"][0]["env"][7]["value"]
        expected_image = f"{self.COMMON_REGISTRY_URL}strimzi-rhel8-operator:{self.STRIMZI_VERSION}"
        self.assertIn(self.EXPECTED_NEWEST_KAFKA_VERSION, env_field)
        self.assertIn(self.EXPECTED_UPGRADE_KAFKA_VERSION, env_field)
        self._assert_yaml_fields(yaml_data, expected_image)

    def test_update_user_deployment(self):
        update_user_deployment(self.USER_OPERATOR_DEPLOYMENT_FILE, self.STRIMZI_VERSION)
        yaml_data = _load_yaml_data(self.USER_OPERATOR_DEPLOYMENT_FILE)
        expected_image = f"{self.COMMON_REGISTRY_URL}strimzi-rhel8-operator:{self.STRIMZI_VERSION}"
        self._assert_yaml_fields(yaml_data, expected_image)

    def test_update_topic_deployment(self):
        update_topic_deployment(self.TOPIC_OPERATOR_DEPLOYMENT_FILE, self.STRIMZI_VERSION)
        yaml_data = _load_yaml_data(self.TOPIC_OPERATOR_DEPLOYMENT_FILE)
        expected_image = f"{self.COMMON_REGISTRY_URL}strimzi-rhel8-operator:{self.STRIMZI_VERSION}"
        self._assert_yaml_fields(yaml_data, expected_image)

    def test_update_drain_cleaner_deployment(self):
        update_drain_cleaner_deployment(self.DRAIN_CLEANER_OPENSHIFT_DEPLOYMENT_FILE, self.STRIMZI_VERSION)
        yaml_data = _load_yaml_data(self.DRAIN_CLEANER_OPENSHIFT_DEPLOYMENT_FILE)
        expected_image = f"{self.COMMON_REGISTRY_URL}drain-cleaner-rhel8:{self.STRIMZI_VERSION}"
        self._assert_yaml_fields(yaml_data, expected_image)

    def test_get_last_year_and_quarter(self):
        expected_year = 2023
        expected_quarter = 4
        year, quarter = get_last_year_and_quarter()
        self.assertEqual(year, expected_year)
        self.assertEqual(quarter, expected_quarter)

    def test_get_current_year_and_quarter(self):
        expected_year = 2024
        expected_quarter = 1
        year, quarter = get_current_year_and_quarter()
        self.assertEqual(year, expected_year)
        self.assertEqual(quarter, expected_quarter)


if __name__ == '__main__':
    unittest.main()
