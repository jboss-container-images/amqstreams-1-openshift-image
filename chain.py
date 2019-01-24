#!/usr/bin/env python
'''########################################################

 FILE: chain.py
 DESC: Builds AMQ Streams images in OSBS

 EXEC: ./chain.py

 DEPS: pip install <dep>
       - yaml

########################################################'''
import argparse
import os 
import re
import shutil
import sys
import threading
import yaml

from chain.build import Build
from chain.traverse import traverse, get_image_name
from chain.hierarchy import create_hierarchy_dict

CHAIN_LOG_DIRECTORY="logs"
CHAIN_LOG_FILE="chain.log"
CONFIG_FILE="config.yaml"

def override(image, build_branch):
  '''
  Given image name (e.g. java-base, etc) and build branch 
  (e.g. 'cp','dev', or 'release'), constructs cekit
  override arguments for writing to/building from specific
  dist-git branches
  
  Example:
    branch: rh-amqstreams-1.0-clusteroperator-openshift-dev-rhel-7
    repo:   containers/amqstreams-1
  '''
  with open(CONFIG_FILE, 'r') as yaml_file:
    data = yaml.load(yaml_file)
  
  override = ""
  osbs_info = data.get("downstream").get('osbs')
  osbs_repo = osbs_info.get("repository")
  osbs_prefix = osbs_info.get("prefix")
  osbs_suffix = osbs_info.get("suffix")
  
  if(build_branch in ['cp', 'dev']):
    osbs_suffix  = osbs_suffix.split("-")
    osbs_suffix.insert(1, build_branch)
    osbs_suffix = "-".join(osbs_suffix)

    osbs_branch = "-".join([osbs_prefix, image.replace("-",""), osbs_suffix])
  
    override = "--overrides {'osbs': {'repository': {'branch': '"\
               + osbs_branch + \
               "', 'name': '"\
               + osbs_repo + \
               "'}}}"
  
  return override

def is_cekit(cmd, image, build_branch):
  ''' If cekit command, return cmd with arguments'''
  if("cekit build" in cmd):
    cmd = cmd + override(image, build_branch)
  
  return cmd

def print_tree(d, indent=0):
  ''' Prints formatted nested dictionary '''
  for key, value in d.items():
    print('  ' * indent + str(key))
    if isinstance(value, dict):
      print_tree(value, indent+1)

class MyParser(argparse.ArgumentParser):

  def error(self, message):
    self.print_help()
    sys.stderr.write('\nError: %s\n' % message)
    sys.exit(2)

class Chain(object):
  """ Class for ordering and executing container builds """
  def __init__(self):
    self.image_list = []
    traverse(os.getcwd(), get_image_name, self.image_list)
    self.build_branch = None
    self.build_type = None
    self.cmd = None
    self.logs_dir = CHAIN_LOG_DIRECTORY
    self.log = self.prep_log(CHAIN_LOG_FILE)

  def prep_log(self, name):
    ''' Creates new logging directory/file for chain builds '''
    if os.path.exists(self.logs_dir):
      shutil.rmtree(self.logs_dir)
    os.makedirs(self.logs_dir)
    return os.path.join(self.logs_dir, name)

  def log_build(self, build, lock):
    ''' Write build info to chain build log '''
    build_info = [build.image] + self.extract_build_info(build)

    lock.acquire()
    with open(self.log, 'a') as f:
      form = '%-25s ' + ('%-10s ' * (len(build_info) - 1))
      formatted_output = form % tuple(build_info)
      f.write(formatted_output + "\n")
    lock.release()

  def extract_build_info(self, build):
    ''' Extracts build information from stdout into list'''
    patterns = [  
      ["taskID",  '(?<=taskID=)([0-9])*'],
      ["buildID", '(?<=buildID=)([0-9])*'],
      ["image",   '(?<=repositories:\n)(.)*'],
      ["imageTag",'(?<=tags:\s)(.)*(?=,)']
    ]
    log_file= os.path.join(CHAIN_LOG_DIRECTORY, build.image + ".log")
    with open(log_file, 'r') as f:
      text=f.read()

    build_info = []
    for name, regex in patterns:
      matches = re.search(regex, text)
      if( matches is not None ):
        build_info.append(matches.group(0))

    if( build.failure ):
      build_info.append("ERROR")

    return build_info

  def chain_build(self, h_dict, lock):
    ''' Recursively executes image builds concurrently in hierarchical order '''
    if(len(h_dict) == 1):
      image  = next(iter(h_dict))
      h_dict = next(iter(h_dict.values()))
      cmd = is_cekit(self.cmd, image, self.build_branch)

      build = Build(image, cmd, lock)
      build.start()
      build.join() # Wait for build to finish

      if(build.image in self.image_list):
        self.log_build(build, lock)

        if(build.failure):
          print("Incomplete " + build.image + " ( Severing dependent builds )" )
          return -1

    threads = []
    for k, v in h_dict.items():
      thread = threading.Thread(target=self.chain_build, args=[{k : v}, lock])
      threads.append(thread)
      thread.start()

    for thread in threads:
      thread.join()

  def parse(self):
    ''' Parses shell arguments '''
    parser = MyParser(
      description='Cekit wrapper for chain builds',
      formatter_class=argparse.RawDescriptionHelpFormatter)

    build_group = parser.add_argument_group('build', "Arguments valid for the 'build' target")
    build_group.add_argument('--build-type',
                               default='local',
                               choices=['local', 'scratch', 'release'],
                               help='an engine used to build the image.')
    build_group.add_argument('--build-branch',
                               default='release',
                               choices=['dev', 'cp', 'release'],
                               help='dist-git branch to push to and build from')
    
    tree_group = parser.add_argument_group('tree', "Arguments valid for the 'tree' target")
    
    images_group = parser.add_mutually_exclusive_group()
    images_group.add_argument('--build-image',
                              default=None,
                              choices=self.image_list,
                              help='image to start chain build')

    parser.add_argument('commands',
                        nargs='+',
                        choices=['build', 'tree'],
                        help="commands that should be executed, \
                             you can specify multiple commands")
    
    self.args = parser.parse_args()
    return self

  def run(self): 
    # Create a hierarchical image dictionary
    h_dict = create_hierarchy_dict(self.args.build_image)
 
    # Command to be run in every image directory
    self.cmd = "cekit build "

    print_tree(h_dict)
    if('build' in self.args.commands):
      self.build_type   = self.args.build_type
      self.build_branch = self.args.build_branch

      if("cekit build " in self.cmd):
        if(self.build_type == 'scratch'):
          self.cmd += '--build-engine=osbs'
        elif(self.build_type == 'release'):
          self.cmd += '--build-engine=osbs --build-osbs-release'

      # For limiting access to shared resources
      lock = threading.Lock()

      print("--- Builds Started ---")
      with open(self.log, 'a') as f:
        f.write("--- Builds Started --- ( %s ) \n" % (self.build_type))

      self.chain_build(h_dict, lock)

      print("--- Builds Complete ---")
      with open(self.log, 'a') as f:
        f.write("--- Builds Complete --- ( %s ) \n" % (self.build_type))

def main():
  chain = Chain()
  chain.parse().run()

if __name__ == '__main__':
  main()
