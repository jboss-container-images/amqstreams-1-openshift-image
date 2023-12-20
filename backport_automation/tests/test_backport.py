#!/usr/bin/env python3
"""########################################################
 FILE: test_backport.py
########################################################"""
import unittest
from unittest.mock import patch
from backport_automation.modules import backport


class TestBackportExampleAutomation(unittest.TestCase):

    def test_create_release_url_for_zips(self):
        release_url = backport.create_release_url_for_zips()
        expected_url = "https://github.com/strimzi/strimzi-kafka-operator/releases/download/0.38.0/strimzi-0.38.0.zip"
        self.assertEqual(release_url, expected_url)

    def test_get_latest_strimzi_release(self):
        result = backport.get_latest_strimzi_release()
        self.assertEqual(result, "0.38.0")  # Adjust this based on the expected latest release

    @patch("os.listdir")
    def test_compare_directory_files_equal(self, mock_listdir):
        mock_listdir.side_effect = [
            ["file1.txt", "file2.txt", "file3.txt"],
            ["file1.txt", "file2.txt", "file3.txt"]
        ]
        with patch("builtins.print") as mock_print:
            backport.compare_directory_files("dir_path1", "dir_path2")
        # Asserting that the print calls contain the expected output
        mock_print.assert_any_call("Number of files in dir_path1: 3")
        mock_print.assert_any_call("Number of files in dir_path2: 3")
        mock_print.assert_any_call("Both directories have the same number of files.")


if __name__ == '__main__':
    unittest.main()
