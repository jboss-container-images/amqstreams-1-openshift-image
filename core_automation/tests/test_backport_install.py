#!/usr/bin/env python3
"""########################################################
 FILE: test_backport_install.py
########################################################"""
import unittest
from datetime import datetime

import yaml

from core_automation.modules.backport_install import (update_deployment,
                                                      update_cluster_operator_deployment,
                                                      get_current_year_and_quarter, get_last_year_and_quarter)


def _load_yaml_data(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)


class TestBackportExampleAutomation(unittest.TestCase):
    RESOURCES_PATH = "resources/"
    COMMON_REGISTRY_URL = "registry.redhat.io/amq-streams/"
    EXPECTED_NEWEST_KAFKA_VERSION = "3.8.0"
    EXPECTED_UPGRADE_KAFKA_VERSION = "3.7.0"
    RHT_COMP_VERSION = "2.8"
    STRIMZI_VERSION = "2.8.0"
    YEAR_AND_QUARTER_VERSION = "2024.Q3"

    def setUp(self):
        self.USER_OPERATOR_DEPLOYMENT_FILE = self.RESOURCES_PATH + "test.05-Deployment-strimzi-user-operator.yaml"
        self.TOPIC_OPERATOR_DEPLOYMENT_FILE = self.RESOURCES_PATH + "test.05-Deployment-strimzi-topic-operator.yaml"
        self.CLUSTER_OPERATOR_DEPLOYMENT_FILE = self.RESOURCES_PATH + "test.060-Deployment-strimzi-cluster-operator.yaml"
        self.DRAIN_CLEANER_OPENSHIFT_DEPLOYMENT_FILE = self.RESOURCES_PATH + "test.060-Deployment-strimzi-drain-cleaner-openshift.yaml"

    def _assert_yaml_fields(self, yaml_data, expected_fields):
        image_field = yaml_data["spec"]["template"]["spec"]["containers"][0]["image"]
        label_field = yaml_data["spec"]["template"]["metadata"]["labels"]
        self.assertEqual(image_field, expected_fields)
        self.assertEqual(label_field["rht.comp_ver"], self.RHT_COMP_VERSION)
        self.assertEqual(label_field["rht.prod_ver"], self.YEAR_AND_QUARTER_VERSION)

    def test_update_cluster_operator_deployment(self):
        update_cluster_operator_deployment(self.CLUSTER_OPERATOR_DEPLOYMENT_FILE, self.STRIMZI_VERSION)
        yaml_data = _load_yaml_data(self.CLUSTER_OPERATOR_DEPLOYMENT_FILE)
        env_field = yaml_data["spec"]["template"]["spec"]["containers"][0]["env"][7]["value"]
        expected_image = f"{self.COMMON_REGISTRY_URL}strimzi-rhel9-operator:{self.STRIMZI_VERSION}"
        self.assertIn(f"registry.redhat.io/amq-streams/kafka-38-rhel9:{self.STRIMZI_VERSION}", env_field)
        self._assert_yaml_fields(yaml_data, expected_image)

    def test_update_user_deployment(self):
        update_deployment(self.USER_OPERATOR_DEPLOYMENT_FILE, self.STRIMZI_VERSION, "user-operator", "infrastructure")
        yaml_data = _load_yaml_data(self.USER_OPERATOR_DEPLOYMENT_FILE)
        expected_image = f"{self.COMMON_REGISTRY_URL}strimzi-rhel9-operator:{self.STRIMZI_VERSION}"
        self._assert_yaml_fields(yaml_data, expected_image)

    def test_update_topic_deployment(self):
        update_deployment(self.TOPIC_OPERATOR_DEPLOYMENT_FILE, self.STRIMZI_VERSION, "topic-operator", "infrastructure")
        yaml_data = _load_yaml_data(self.TOPIC_OPERATOR_DEPLOYMENT_FILE)
        expected_image = f"{self.COMMON_REGISTRY_URL}strimzi-rhel9-operator:{self.STRIMZI_VERSION}"
        self._assert_yaml_fields(yaml_data, expected_image)

    def test_update_drain_cleaner_deployment(self):
        update_deployment(self.DRAIN_CLEANER_OPENSHIFT_DEPLOYMENT_FILE, self.STRIMZI_VERSION, "drain-cleaner",
                          "application")
        yaml_data = _load_yaml_data(self.DRAIN_CLEANER_OPENSHIFT_DEPLOYMENT_FILE)
        expected_image = f"{self.COMMON_REGISTRY_URL}drain-cleaner-rhel9:{self.STRIMZI_VERSION}"
        self._assert_yaml_fields(yaml_data, expected_image)

    def test_get_last_year_and_quarter(self):
        current_date = datetime.now()
        current_year = current_date.year
        current_month = current_date.month

        # Calculate expected year and quarter based on current date
        if current_month <= 3:
            expected_year = current_year - 1
            expected_quarter = 4
        elif current_month <= 6:
            expected_year = current_year
            expected_quarter = 1
        elif current_month <= 9:
            expected_year = current_year
            expected_quarter = 2
        else:
            expected_year = current_year
            expected_quarter = 3

        year, quarter = get_last_year_and_quarter()
        self.assertEqual(year, expected_year)
        self.assertEqual(quarter, expected_quarter)

    def test_get_current_year_and_quarter(self):
        current_date = datetime.now()
        current_year = current_date.year
        current_month = current_date.month

        if current_month <= 3:
            expected_year = current_year
            expected_quarter = 1
        elif current_month <= 6:
            expected_year = current_year
            expected_quarter = 2
        elif current_month <= 9:
            expected_year = current_year
            expected_quarter = 3
        else:
            expected_year = current_year
            expected_quarter = 4

        year, quarter = get_current_year_and_quarter()
        self.assertEqual(year, expected_year)
        self.assertEqual(quarter, expected_quarter)


if __name__ == '__main__':
    unittest.main()
