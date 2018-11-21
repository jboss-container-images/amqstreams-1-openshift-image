import os
import yaml

def upstream_name(name, image_list):
  ''' Given downstream image name returns upstream image name'''
  n = name.split("/")[-1]

  if(len(n.split("-")) > 2):
    n = n.split("-")[1]

  for i in image_list:
    if(n == i.replace("-","")):
      return i

  return n

def get_image_name(path, image_list):
  ''' Appends directories containing image descriptor files to list '''
  if(os.path.basename(path) == 'image.yaml'):
    image_name = os.path.basename(os.path.dirname(path))
    image_list.append(image_name)
    return True
  return False

def get_image_base(path, image_list, rank_list):
  ''' Extracts image name and basename from image descriptor file '''
  if(os.path.basename(path) == "image.yaml"):
    with open(path, 'r') as yaml_file:
      data = yaml.load(yaml_file)
 
      name = upstream_name(data["name"], image_list)
      base = upstream_name(data["from"], image_list)

      rank_list.append([base, name])
    return True
  return False

def traverse(path, function, *args):
  ''' Recursively traverses path, applying function to all files '''
  if(function(path, *args) or os.path.isfile(path) or os.path.basename(path) == 'target' ):
    return 0
  files = [os.path.join(path, f) for f in os.listdir(path)]
  for f in files:
    traverse(f, function, *args)
