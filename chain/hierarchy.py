import os
from chain.traverse import traverse, get_image_name, get_image_base

def rank_to_hierarchy_dict(image_list):
  ''' Given 2D list of [basename, imagename] pairs, 
      build and return hierarchical dict '''
  h_dict = {}

  for image in image_list:
    if(not hierarchy(image, h_dict)):
      h_dict.update( { image[0] : { image[1] : {} } } )

  return h_dict

def rank(image_list, image):
 ''' Returns number of images the given image is based upon '''
 for n, b in image_list:
   if(image == b):
     return rank(image_list, n) + 1
 return 1

def prune_dict(image, matrix):
  ''' Returns dependency tree of specified image '''
  for k,v in matrix.items():
    if(image == k):
      return {k : v}
    else:
      dep_tree = prune_dict(image, v)
      if(dep_tree):
        return dep_tree

def count_images(h_dict):
  ''' Returns number of images in hierarchical dictionary '''
  count = 0
  for k,v in h_dict.items():
    if(v == {}):
      count += 1
    else:
      count += count_images(v) + 1

  return count

def hierarchy(image, h_dict):
  ''' Organizes image into a nested hierarchical dictionary '''
  for k,v in h_dict.items():
    if(image[0] == k):
      h_dict[k].update( { image[1] : {} } )
      return True
    else:
      if(hierarchy(image, v)):
        return True

def create_hierarchy_dict(build_image):
  ''' Returns hierarchical dictionary '''
  image_list = [] 
  rank_list = []

  traverse(os.getcwd(), get_image_name, image_list)

  # Traverse filesystem, collecting images name/base
  traverse(os.getcwd(), get_image_base, image_list, rank_list)

  # Sort images by rank ( number of images layered ontop of )
  rank_list = sorted(rank_list, key=lambda image:rank(rank_list, image[0]))

  # Create hierarchical dictionary based on rank
  h_dict = rank_to_hierarchy_dict(rank_list)

  if build_image is not None:
    # Prune dictionary to only specified image tree  
    h_dict = prune_dict(build_image, h_dict)

  return h_dict
