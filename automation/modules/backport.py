#!/usr/bin/env python3
"""########################################################
 FILE: backport.py
########################################################"""
import os
import shutil
import urllib.request
import zipfile


# Create a URL for downloading the zip
def create_release_url_for_zips(release):
    return "https://github.com/strimzi/strimzi-kafka-operator/releases/download/" + release + "/strimzi-" + release + ".zip"


# Unpack the zip locally, into our local example - elsewhere
def unpack_zips(release):
    url = create_release_url_for_zips(release)
    contents = urllib.request.urlopen(url).read()
    with open("../strimzi.zip", 'wb') as file:
        file.write(contents)
    with zipfile.ZipFile("../strimzi.zip", 'r') as strimzizip:
        strimzizip.extractall(".")


# Compare number of files from upstream to downstream
def compare_directory_files(dir_path1, dir_path2):
    try:
        files_in_dir1 = os.listdir(dir_path1)
        files_in_dir2 = os.listdir(dir_path2)
        num_files_dir1 = len(files_in_dir1)
        num_files_dir2 = len(files_in_dir2)
        print(f"Number of files in {dir_path1}: {num_files_dir1}")
        print(f"Number of files in {dir_path2}: {num_files_dir2}")
        if num_files_dir1 == num_files_dir2:
            print("Both directories have the same number of files.")
        else:
            print("The number of files in the directories is different.")
    except FileNotFoundError as e:
        print(f"Error: {e}")


# String replacement in files for Kafka versions
def replace_version_in_files(directory, file_extensions, version_to_replace, replacement, version_type):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(file_extensions):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    content = f.read()
                if version_type == "kafka":
                    content = content.replace(version_to_replace, str(replacement))
                elif version_type == "inter_broker_protocol":
                    content = content.replace(version_to_replace, str(replacement))
                with open(file_path, 'w') as f:
                    f.write(content)


# String replacement in files for Streams
def string_replacement(examples_dir, file_name):
    readme_file_path = os.path.join(examples_dir, file_name)
    try:
        with open(readme_file_path, 'r') as f:
            content = f.read()
        content = content.replace('Strimzi', 'AMQ Streams').replace('strimzi', 'AMQ Streams')
        content = content.replace('* JMX Trans deployment', '')
        with open(readme_file_path, 'w') as f:
            f.write(content)
        print(f'Replacement and removal in {readme_file_path} completed successfully.')
    except Exception as e:
        print(f'Error modifying text in {readme_file_path}: {e}')


# delete directory that should not be copied
def delete_excluded_directory(folder_name, module_name, strimzi_dir):
    target_dir = os.path.join(strimzi_dir, module_name)
    delete_folder = os.path.join(target_dir, folder_name)
    try:
        shutil.rmtree(delete_folder)
        print(delete_folder + ' folder deleted successfully.')
    except FileNotFoundError:
        print('Target folder not found.')
    except Exception as e:
        print('Error deleting folder:', e)


# delete file(s) before copying upstream directory to downstream directory
def delete_file(*file_paths):
    for file_path in file_paths:
        try:
            os.remove(file_path)
            print(f'Successfully deleted file: {file_path}')
        except OSError as e:
            print(f'Error deleting file {file_path}: {e}')


# copy upstream directory to downstream directory
def copy_directory(source_name, dest_name, strimzi_dir):
    source_dir = os.path.join(strimzi_dir, source_name)
    dest_dir = f'../{dest_name}'
    try:
        shutil.copytree(source_dir, dest_dir,
                        dirs_exist_ok=True)  # Copy the contents of the source directory to the destination
        print(f'{source_name} directory copied to {dest_name} successfully.')
    except Exception as e:
        print(f'Error copying {source_name} directory to {dest_name}:', e)


# delete imported upstream resources
def delete_created_upstream_resources(strimzi_dir):
    strimzi_zip = "../strimzi.zip"
    try:
        shutil.rmtree(strimzi_dir)
        print(f'Deleted {strimzi_dir} directory successfully.')
        if os.path.exists(strimzi_zip):
            os.remove(strimzi_zip)
            print(f'Deleted {strimzi_zip} file successfully.')
        else:
            print(f'{strimzi_zip} file not found. No deletion performed.')
    except Exception as e:
        print(f'Error deleting resources: {e}')
