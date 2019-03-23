import subprocess
import threading
import traceback

from chain.build import Build
from chain.hierarchy import create_hierarchy_dict
from chain.generator import generate_descriptor
from chain.logging   import log_build

class Builder(object):
    """
    Class representing generic builder - if its instantiated it returns proper builder
    """
    def __new__(cls, config):
        if cls is Builder:
            if 'dev' == config.build_type:
                # import is delayed until here to prevent circular import error
                from chain.builders.docker import DockerBuilder as BuilderImpl
            elif 'scratch' == config.build_type or 'release' == config.build_type:
                # import is delayed until here to prevent circular import error
                from chain.builders.osbs import OSBSBuilder as BuilderImpl
            else:
                raise Exception("Builder type %s is not supported" % config.build_type)

            return super(Builder, cls).__new__(BuilderImpl)

    def __init__(self, config):
        self.config = config
        self.h_dict = config.h_dict 

    def check_kerberos_authentication(self):
        try:
            process = subprocess.Popen(['klist'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            if(process.returncode):
                raise Exception('Missing kerberos ticket. Run "kinit <user>@REDHAT.COM"')
        except Exception as e:
            print(traceback.format_exc())
            raise Exception('Failed to get kerberos credentials')

    def check_prerequistites(self):
        self.check_kerberos_authentication()
    
    def build(self, build_args):
        raise Exception("Buider.build() is not implemented!")

    def chain_build(self, h_dict, lock):
        ''' Recursively executes image builds concurrently in hierarchical order '''
        if(len(h_dict) == 1):
            image  = next(iter(h_dict))
            h_dict = next(iter(h_dict.values()))
            cmd = self.config.cmd

            if(not image.trunk_image):
              generate_descriptor(image, self.config)
              build = Build(image, self.config, lock)
              build.start() 
              build.join() # Wait for build to finish
            
              log_build(build, lock)

              if(build.failure):
                print("Incomplete " + image.name + " ( Severing dependent builds )" )
                return -1

        threads = []
        for k, v in h_dict.items():
            thread = threading.Thread(target=self.chain_build, args=[{k : v}, lock])
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join() 
