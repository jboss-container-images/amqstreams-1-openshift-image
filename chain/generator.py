'''########################################################

 FILE: generator.py
 DESC: Updates image descriptor file before the image is 
       built. Contains a lot of temporary hard coded changes
       specific to the 1.1.0 release. 
    
########################################################'''
import os
import ruamel.yaml
import sys
import copy

from ruamel import yaml
from shutil import copyfile

def create_help_md(image):
    ''' Create help.md file '''
    h_path = os.path.join(image.src_path, "help.md")
    with open(h_path) as f:
        lines = f.readlines()
    
    if(len(lines)>0):
        lines[0] = "% " + image.product_name + " (1) Container Image Pages\n"

    with open(h_path, "w") as f:
        f.writelines(lines)

def create_multi_version_files(image):
    ''' Copy template files into versioned directory for
        multi versioned images '''
    if(image.multi_version):
        ver = image.kafka_version
        src = image.src_path
        des = image.path

        if not os.path.exists(image.path):
            os.makedirs(des)

        for f in ["image.yaml", "help.md"]:
            copyfile(os.path.join(src,f), os.path.join(des, f))    

def add_override(src, config):
    if(config.build_branch in ['dev', 'cp']):
        branch = src["osbs"]["repository"]["branch"].replace("rhel", config.build_branch + "-rhel") 

        override = " --overrides {'osbs': {'repository': {'branch': '"\
            + branch + \
            "', 'name': '"\
            + src["osbs"]["repository"]["name"] + \
            "'}}}"
        
        config.cmd += override 

def generate_descriptor(image, config):
    ''' Updates image descriptor file to image specifications '''
    create_help_md(image)   
    create_multi_version_files(image)
    
    # Update descriptor fields    
    with open(image.full_path) as f:
        src = yaml.load(f, Loader=ruamel.yaml.RoundTripLoader, preserve_quotes=True)

    add_override(src, config)
    
    src["name"] = image.product_name
    src["from"] = image.product_base

    if(image.multi_version):
        ver = image.kafka_version
        if(config.build_type == "dev"):
            src["version"] = config.product_version + "-" + ver
        else:
            src["version"] = config.product_version + "_" + ver.replace("-","_")

        if(image.parent_image.multi_version):
            if(config.build_type == "dev"):
                src["from"] = image.product_base + "-" + ver
            else:
                src["from"] = image.product_base + "_" + ver.replace("-","_")
      
        # Point versioned descriptor to common modules directory
        repos = src["modules"]["repositories"]
        for r in range(len(repos)):
            repo = repos[r]
            if("path" in repo.keys()):
                repo["path"] = '../modules'
    else:
        # Update jars for non multi versioned images
        if(image.upstream_name in config.jars):
            image.jar = config.jars.get(image.upstream_name).jars
        else:
            image.jar = {}
    
    # Update artifacts section
    if("artifacts" in src):
        for artifact in src['artifacts']:
            for jar in image.jar:
                if(jar.name == artifact.get("name")):
                    for attr, value in jar.__dict__.items():
                       artifact.update( { attr:value } )
                       if(value is None):
                           del artifact[attr]
                    if('version' in artifact): 
                       del artifact['version']

    # Update com.redhat.component label 
    kn = image.kafka_version.split("-")[-1].replace(".","")
    kk = lambda x: "-" + x if x else ""

    new_label = "amqstreams11-" + image.upstream_name.replace("-","") + kk(kn) + "-openshift-container"
    for label in src["labels"]:
        if("com.redhat.component" in label.values()):
            label.update( { "value": new_label } )
    # envs
    if("envs" in src): 
        for label in src["envs"]:
            if("COM_REDHAT_COMPONENT" in label.values()):
                label.update( { "value": new_label } )

    # Update dist-git branch
    kv = lambda x: "-" + x if x else ""
    branch_name = "rh-amqstreams-1.1-" + image.upstream_name.replace("-","") \
                                       + kv(image.kafka_version_number) \
                                       + "-openshift-rhel-7"
    src["osbs"]["repository"]["branch"] = branch_name
    
    # Update target value
    image.target = src["osbs"]["repository"]["branch"].replace("-openshift","") + "-containers-candidate"
    # Setting KAKFA_VERSION env var
    if("envs" in src):
        vv = image.kafka_version_number
        for env in src["envs"]:
            if("KAFKA_VERSION" in env.values()):
                env.update( { "value": vv } )
 
    yml = yaml.YAML()
    yml.indent(mapping=2, sequence=4, offset=2)

    # Update descriptor file 
    with open(image.full_path, "w") as f:
        yml.dump(src, f)
