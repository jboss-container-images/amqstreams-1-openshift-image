#!/usr/bin/env python3
from modules import constants
from modules.file import File
from modules.bundle_automation import BundleAutomation

import koji as brew
import os

def main():
  brew_client = brew.ClientSession(os.environ['BREW_URL'])

  cluster_service_version_file = File(os.environ['DIST_GIT_CSV_FILE_PATH'])
  component_data = BundleAutomation.collect_component_build_info()
  product_version = BundleAutomation.get_product_version(cluster_service_version_file.data)

  # Get old to new tag mappings
  tag_dict = BundleAutomation.create_tag_dict_from_new_csv_format(brew_client, cluster_service_version_file.data, component_data)
  bundle_versions = BundleAutomation.generate_bundle_version_strings(
          brew_client, 
          cluster_service_version_file.data,
          product_version
  )

  # Update CSV with new pull_specs + bump bundle version
  cluster_service_version_file.data = BundleAutomation.update_csv_data(cluster_service_version_file.data, bundle_versions, tag_dict)
  cluster_service_version_file.write(os.environ['DIST_GIT_CSV_FILE_PATH'])
  cluster_service_version_file.write(os.environ['GIT_HUB_CSV_FILE_PATH'])

  print(
    "Product version:", product_version, 
    "Old bundle version", bundle_versions[constants.OLD_BUNDLE_VERSION_INDEX], 
    "New bundle version:", bundle_versions[constants.NEW_BUNDLE_VERSION_INDEX]
  )

  with open("csv_version", 'w') as sources:
    sources.write(bundle_versions[constants.NEW_BUNDLE_VERSION_INDEX])

if __name__ == "__main__":
  main()
