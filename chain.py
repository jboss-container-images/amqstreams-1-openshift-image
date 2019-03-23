#!/usr/bin/env python3
'''########################################################

 FILE: chain.py
 DESC: Builds all images in order
 
 DEPS: pip3 install -r requirements.txt
 EXEC: ./chain.py

########################################################'''
import argparse
import os 
import sys
import yaml

from chain.config import Config
from chain.builder import Builder
from chain.hierarchy import create_hierarchy_dict
from chain.builders.osbs import OSBSBuilder
from chain.registry_loader import RegistryLoader

class MyParser(argparse.ArgumentParser):
    def error(self, message):
        self.print_help()
        sys.stderr.write('\nError: %s\n' % message)
        sys.exit(2)

def str2bool(v):
    # Credit: https://stackoverflow.com/questions/15008758/parsing-boolean-values-with-argparse
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

class Chain(object):
    """ Class for ordering and executing container builds """
    def __init__(self):
        self.image_list = []
   
    def parse(self):
        ''' Parses shell arguments '''
        parser = MyParser(
            description='Cekit wrapper for chain builds',
            formatter_class=argparse.RawDescriptionHelpFormatter)

        build_group = parser.add_argument_group('build', "Arguments valid for the 'build' target")
        build_group.add_argument('--build-type',
                               default='dev',
                               choices=['dev', 'scratch', 'release'],
                               help='type of build being executed')
        build_group.add_argument('--build-branch',
                               default='release',
                               choices=['dev', 'cp', 'release'],
                               help='dist-git branch to push to and build from')
    
        push_group = parser.add_argument_group('push', "Arguments valid for the 'push' target")
        push_group.add_argument('--cluster',
                               default='local',
                               choices=['local', 'remote'],
                               help='cluster registry to push images')
    
        images_group = parser.add_argument_group("Arguments valid for tree, build, and push targets")
        images_group.add_argument('--build-image',
                                 default=None,
                                 help='image to start chain build')
        images_group.add_argument('--build-children',
                                type=str2bool, nargs='?',
                                const=True,
                                default=True,    
                                choices=[True, False],
                                help='build children images')
        images_group.add_argument('--build-children-only',  
                                type=str2bool, nargs='?',
                                const=True, 
                                default=False,
                                choices=[True, False],
                                help='build image\'s children images only')

        parser.add_argument('commands',
                          nargs='+',
                          choices=['tree', 'build', 'push'],
                          help="commands that should be executed, \
                                you can specify multiple commands")
    
        self.args = parser.parse_args()
        return self
      
    def run(self): 
        config = Config(self.args)
 
        h_dict = create_hierarchy_dict(config)
        config.h_dict = h_dict
  
        if('build' in self.args.commands):
            chain = Builder(config)
            chain.build()
   
        if('push' in self.args.commands):
            loader = RegistryLoader(config)
            loader.push_images()        
    
def main():
    chain = Chain()
    chain.parse().run()

if __name__ == '__main__':
    main()
