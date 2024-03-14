#!/usr/bin/env python3
"""########################################################
 FILE: test_backport_examples.py
########################################################"""
import os
from unittest.mock import patch
import unittest

from automation.modules.backport_examples import compare_directory_files, update_example_dir_readme, \
    delete_created_upstream_resources, delete_file, create_release_url_for_zips


class TestBackportExampleAutomation(unittest.TestCase):

    def test_create_release_url_for_zips(self):
        target_strimzi_version = "0.38.0"
        release_url = create_release_url_for_zips(target_strimzi_version)
        expected_url = "https://github.com/strimzi/strimzi-kafka-operator/releases/download/0.38.0/strimzi-0.38.0.zip"
        self.assertEqual(release_url, expected_url)

    @patch("os.listdir")
    def test_compare_directory_files_equal(self, mock_listdir):
        mock_listdir.side_effect = [
            ["file1.txt", "file2.txt", "file3.txt"],
            ["file1.txt", "file2.txt", "file3.txt"]
        ]
        with patch("builtins.print") as mock_print:
            compare_directory_files("dir_path1", "dir_path2")

        mock_print.assert_any_call("Number of files in dir_path1: 3")
        mock_print.assert_any_call("Number of files in dir_path2: 3")
        mock_print.assert_any_call("Both directories have the same number of files.")

    def test_string_replacement(self):
        examples_dir = "examples"
        file_name = "README.md"
        update_example_dir_readme(examples_dir, file_name)
        with open("../../examples/README.md", 'r') as f:
            content = f.read()
        self.assertIn("AMQ Streams", content)

    def test_excluded_directory(self):
        directory = "strimzi-0.38.0/examples"
        excluded_directory = "strimzi-0.38.0/examples/kafka-mirror-maker-2"
        delete_created_upstream_resources(directory)
        self.assertFalse(os.path.exists(excluded_directory))

    def test_deleted_files(self):
        file_path1 = "strimzi-0.38.0/examples/security/keycloak-authorization/README.md"
        file_path2 = "strimzi-0.38.0/examples/connect/kafka-connect-build.yaml"
        delete_file(file_path1, file_path2)
        self.assertFalse(os.path.exists(file_path1))
        self.assertFalse(os.path.exists(file_path2))

    def test_deleted_upstream_resource(self):
        directory = "strimzi-0.38.0"
        delete_created_upstream_resources(directory)
        self.assertFalse(os.path.exists(directory))


if __name__ == '__main__':
    unittest.main()
