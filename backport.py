'''########################################################

 FILE: backport.py
 DESC: Backports upstream container images to downstream,
       backporting deployment files
       and scripts to downstream format.

 EXEC: python backport.py

 TODO:
    - Generating image descriptor files and base modules
      or new images
    - COMPLETE CONFIG WITH NEW FOUND DATA AND STORE
    - Detect hierarchy
    - Check changed image bases
    - dependency changes

 DEPS: pip install <dep>
    - yaml
    - git
    - yamlloader
    - OrderedDict

########################################################'''
import git
import re
import shutil
import distutils.dir_util
import yaml
import yamlloader
from collections import OrderedDict
from os import listdir, getcwd
from os.path import isfile, join, exists, basename

# File containing container repo and naming details
CONFIG="./config.yaml"

# Currently, there are two different dynamic_resources.sh
# One for upstream and one for downstream. The images in the
# images listed in the EXEMPTION list use the downstream
# dynamic_resources.sh so we don't want to overwrite it with
# the upstream scripts. This is temporary until we move
# the downstream script upstream
EXEMPTIONS = ["java-base", "test-client"]
SPECIAL_CASE = {"s2i" : "kafka-connect-s2i"}
DOCKER_KEYWORDS=["ADD", "ARG", "CMD", "COPY", "ENV", "EXPOSE", "FROM", "RUN", "USER", "WORKDIR"]

def swap_words(text, word_dict):
  ''' Replaces all words in text with word_dict value '''
  for key in word_dict:
    if(key in text):
      print("CHANGED: " + key + " ---> " + word_dict[key])
      text = text.replace(key, word_dict[key])
  return text

def remap_words(path, word_dict):
  ''' Replaces all words in file f with word_dict value '''
  if(isfile(path)):
    print(path)
    with open(path, 'r') as file:
      text = swap_words(file.read(), word_dict)
    with open(path, 'w') as file:
      file.write(text)
    return True
  return False

def parse_dockerfile(dockerfile):
  ''' Returns dictionary of parsed Docker values '''
  dict={}
  comment_block=False
  with open(dockerfile, 'r') as file:
    for word in file.read().replace('\n', ' ').split(" "):
      if(word in DOCKER_KEYWORDS):
        key=word
        if key not in dict:
          dict[key]=[]
        comment_block=False
      else:
        if(word == "#"):
          comment_block = True
        elif(word != "" and not comment_block):
          dict[key].append(word)

  # TODO scripts should be handled modular scripts
  del dict['COPY']
  return dict

def get_packages(ls):
  ''' Returns list of rpm packages from list '''
  lst = " ".join(ls)
  p_string = re.search(r"(?<=install )(.*?)(?= &&)", lst).group(0)
  p_list = p_string.split(" ")

  return p_list

# WIP
def productize_dict(path, dict):
  config = yaml.load(open(CONFIG))["downstream"]
  # MAP YAML AND DOCKER DICTIONARIES TOGETHER
  downstream_map=get_image_dict()
  base = basename(path)
  map = { "NAME": "name",
          "DESCRIPTION": "description",
          "ENV":  "envs",
          "INSTALL": "install",
          "FROM": "from",
          "LABELS": "labels",
          "VERSION": "version",
          "WORKDIR": "workdir"
        }

  dict["NAME"]    = format_name(base, "downstream")
  dict["DESCRIPTION"] = "AMQ Streams image for " + base
  dict["FROM"]    = downstream_map.get(dict["FROM"][0])
  dict["VERSION"] = config["tag"]
  component = [config["prefix"], base.replace("-", ""), "openshift-container"]
  dict["LABELS"] = {"com.redhat.component": "-".join(component)}
  dict["com.redhat.component"] =  "-".join(component)
  dict["INSTALL"] = get_packages(dict["RUN"])

  # Map keys to match image desciptor file keys
  for k,v in map.iteritems():
    dict[v] = dict.pop(k)

  return dict

def recurse_dict(temp, data):
  ''' Check/append ports too'''
  if(len(temp) == 2):
    key = temp.get("name")
    if(key in data):
      print(key)
      temp["value"] = data[key]
    return temp

  for k,v in temp.iteritems():
    if(k in data):
      if(isinstance(v, str)):
        temp[k] = data[k]
      elif(isinstance(v, dict)):
        print(k)
      elif(isinstance(v, list)):
        for i in v:
          recurse_dict(i, data)

  return temp

# WIP
def generate_image_descriptor(path):
  '''Converts Dockerfile into image desciptor file '''
  # If downstream image.yaml doesn't exist, generate it
  # Split into list
  # Parse template file
  # Generate updated values
  docker_dict = productize_dict(path, parse_dockerfile(join(path, "Dockerfile")))

  #for d,v in docker_dict.iteritems():
  #   print(d,v)

  ###############################
  # Generate yaml
  ##############################
  # Figure out how preserve lines
  with open('template.yaml') as yaml_file:
    data = yaml.load(yaml_file, Loader=yamlloader.ordereddict.CLoader)

  dd = recurse_dict(data, docker_dict)
  #for k,v in dd.iteritems():
  #  print(k, v)

  with open('result.yml', 'w') as yaml_file:
   yaml.dump(data, yaml_file, default_flow_style=False, Dumper=yamlloader.ordereddict.CDumper)

  #print( yaml.dump(data, default_flow_style=False,  Dumper=yamlloader.ordereddict.CDumper) )
  # Generate modules install script

  return 0

# Recurse to set dictionary value
def nest_dict():

  return 0

def remap_scripts(path):
  ''' Overwrites downstream scripts with upstream scripts '''
  base = basename(path)
  if(isfile(path)):
    return True
  elif(exists(join(path, "Dockerfile")) and base not in EXEMPTIONS):
    upstream   = join(path, "scripts")
    downstream = join(getcwd(), base, "modules", base, "scripts")

    if(base in SPECIAL_CASE):
      base = SPECIAL_CASE.get(base)
      downstream = join(getcwd(), base, "modules", base, "scripts")

    if(exists(upstream)):
      distutils.dir_util.copy_tree(upstream, downstream)
    
    return False
  return False

def traverse(path, function, *args):
  ''' Recursively traverses path, applying function to all files '''
  if(function(path, *args)):
    return 0
  files = [join(path, f) for f in listdir(path)]
  for f in files:
    traverse(f, function, *args)

def clone(dest):
  ''' Clones upstream repo into dest directory '''
  if(exists(dest)):
    print("Reusing existing upstream clone: ", dest)
  else:
    config = yaml.load(open(CONFIG))["upstream"]
    src    = config["git_repo"]
    branch = config["branch"]
    repo = git.Repo.clone_from(src, dest, branch=branch)

def format_name(name, source):
  ''' Returns formated upstream or downstream image name '''
  config = yaml.load(open(CONFIG))[source]

  if(source == "downstream"):
    name = name.replace("-", "")

  iname = "-".join(filter(None, [config["prefix"], name, config["suffix"]]))
  fname = "/".join(filter(None, [config["registry"], config["family"], iname]))
  tname = ":".join([fname, config["tag"]])

  return tname

def get_image_dict():
  ''' Returns dictionary of upstream to downstream image names '''
  config = yaml.load(open(CONFIG))
  image_dict = {}
  # Scan upstream directory and build separate list
  for name in config["images"]:
    upstream   = format_name(name, "upstream")
    downstream = format_name(name, "downstream")
    image_dict[upstream] = downstream

  # TODO Abstract this
  image_dict["centos:7"] = "jboss/base-rhel7:1.1"
  return image_dict

def backport():
  dest="./upstream_clone"
  examples_dir="./examples"

  # Clone upstream repo
  clone(dest)
  
  # Overwrite downstream examples files with upstream examples files
  distutils.dir_util.copy_tree(join(dest, examples_dir), examples_dir)

  # Make dictionary mapping of upstream image names to downstream names
  image_dict = get_image_dict()

  # Change upstream image names to downstream image names in examples
  traverse(examples_dir, remap_words, image_dict)

  # overwrite downstreams scripts with upstream scripts
  traverse(dest, remap_scripts)

  # Remove cloned upstream repo
  shutil.rmtree(dest)

backport()
