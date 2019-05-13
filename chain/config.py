import itertools
import os
import pexpect
import shutil
import yaml

from kubernetes import client, config
from openshift.dynamic import DynamicClient
    
def find(element, d):
  ''' Recursively searches dict for element,
      returns value of element on success,
      returns None on failure '''
  if(d is not None):
      for key, value in d.items():
          if(key == element):
              return value
          elif(isinstance(value, dict)):
              find(element, value)

def find_in_dicts(element, d1, d2):
    ''' Searches two dictionaries for element, 
        and returns element on success, returns
        None on failure  '''
    value =  find(element, d1)
    if(value):
        return value
    return find(element, d2)

class Config():
    def __init__(self, params={}):

        self.log_dir = "logs"
        self.log = self.prep_log("chain.log")

        public_config  = self.open_config("./config.yaml")
        private_config = self.open_config(os.path.expanduser("~/.chain/config.yaml"))
        self.cluster = Cluster(public_config, private_config, params)
        
        self.jars = self.extract_jars(find_in_dicts("jars", public_config, private_config))
        self.product_version = find_in_dicts("downstream", public_config, private_config)["version"] 

        self.h_dict = None
        self.osbs_build = False
       
        # User parameters 
        self.build_type   = params.build_type
        self.build_image  = params.build_image
        self.build_branch = params.build_branch

        # Command to be run in all image directories
        self.cmd = self.build_command(self.build_type)

        self.build_children      = params.build_children
        self.build_children_only = params.build_children_only
        
    def open_config(self, path):
        if(os.path.isfile(path)):
            with open(path, 'r') as yaml_file:
                return yaml.load(yaml_file, Loader=yaml.FullLoader)

    def build_command(self, build_type):
        cmd = "cekit build "
        if(build_type == 'osbs'):
            cmd += '--build-engine=osbs'
            self.osbs_build = True
        elif(build_type == 'release'):
            cmd += '--build-engine=osbs --build-osbs-release'
            self.osbs_build = True
        return cmd

    def prep_log(self, name):
        ''' Creates new logging directory/file for chain builds '''
        if os.path.exists(self.log_dir):
            shutil.rmtree(self.log_dir)
            os.makedirs(self.log_dir)
        return os.path.join(self.log_dir, name)

    def extract_jars(self, jar_metadata):
        ''' Refactor '''
        jars = {}
        attr = ['name', 'version', 'md5', 'url']

        for image in jar_metadata.items():
            jar_tag = JarTag()
            jar_tag.name = image[0]
            for jar_datum in image[1]:
                jar = Jar()
                for a in attr:
                    if(a in jar_datum.keys()):
                        setattr(jar, a, jar_datum.get(a))
                jar_tag.jars.append(jar)
            # Add jar combinations
            count = {}
            for j in jar_tag.jars:
              if(j.name in count):
                 jar_tag.multi_version = True
              
              count.update( { j.name : {} })
            
            if(jar_tag.multi_version):
                jar_combos = itertools.combinations(jar_tag.jars, len(count))
                for jc in jar_combos:
                    no_dup = list({v.name:v for v in list(jc)}.values())
                    if(len(no_dup) == len(count)):
                      kafka_version = ''
                      for d in no_dup:
                        if("kafka" in d.name):
                          kafka_version = d.version
                      jar_tag.combination.update( { kafka_version: no_dup } )
            
            jars.update( { jar_tag.name : jar_tag } )

        return jars

class Jar(object):
    def __init__(self):

        self.name    = None
        self.version = None
        self.md5     = None
        self.url     = None

class JarTag():
    def __init__(self):
        self.name = None
        self.jars = []

        self.multi_version        = False
        self.multi_version_list   = []
        self.num_of_versions      = 0
        self.combination          = {}

class Cluster():

    def __init__(self, public_config, private_config, params={}):
        self.cluster_type = params.cluster
        
        c1 = find("cluster", public_config)
        c2 = find("cluster", private_config)

        c1 = c1[self.cluster_type] if c1 else None
        c2 = c2[self.cluster_type] if c2 else None

        self.url       = find_in_dicts("url", c1, c2)
        self.user      = find_in_dicts("user", c1, c2)
        self.password  = find_in_dicts("password", c1, c2)
        self.namespace = find_in_dicts("namespace", c1, c2)
        self.registry  = find_in_dicts("registry", c1, c2)
        self.token = None
   
    def authenticate(self):
        if(self.cluster_type  == "local"):
            self.authenticate_openshift_instance()
        k8s_client = config.new_client_from_config()
        dyn_client = DynamicClient(k8s_client)

        # Get session token from OpenShift instance
        self.token = k8s_client.configuration.api_key['authorization'].split()[-1]
   
    def get_registry(self, cli):
        v1_services = cli.resources.get(api_version='v1', kind='Service')
        items = v1_services.get(namespace='default', label_selector='docker-registry=default')["items"]
        registry_ip = items[0]['spec']["clusterIP"]
        registry = registry_ip +  ":5000"
        return registry

    def authenticate_openshift_instance(self):
        ''' Logs into OpenShift instance specified by url
            
            Basic auth not supported by kubernetes client library

            TODO: Rewrite
        '''
        #urllib3.disable_warnings()

        child = pexpect.spawn('oc login ' + self.url)
        child.expect('Username:')
        child.sendline(self.user)
        child.expect('Password:')
        child.sendline(self.password)
        child.wait()

        if(child.exitstatus):
          raise Exception('Failed to authenticate to ', url)
