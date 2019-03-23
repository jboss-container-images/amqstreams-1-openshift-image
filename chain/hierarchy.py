import os
import copy

from chain.traverse import traverse, get_images
from chain.image import Image

def print_tree(d, indent=0):
    ''' Prints formatted nested dictionary '''
    for key, value in d.items():
        print('  ' * indent + str(key.tree_name))
        if isinstance(value, dict):
            print_tree(value, indent+1)

def rank_to_hierarchy_dict(image_list):
    ''' Given Image objects, build and return
        a hierarchical dict '''
    h_dict = {}

    for image in image_list:
        if(not hierarchy(image, h_dict)):
            h_dict.update( { image : {} } )
    return h_dict

def hierarchy(image, h_dict):
    ''' Organizes image into a nested hierarchical dictionary '''
    for k,v in h_dict.items():
        if(image.tree_base == k.tree_name):
            image.parent_image = k
            h_dict[k].update( { image : {} } )
            return True
        else:
            if(hierarchy(image, v)):
                return True

def rank(image_list, image):
   ''' Returns number of images the given image is based upon '''
   for i in image_list:
       if(image == i.tree_base):
           return rank(image_list, i.tree_name) + 1
   return 1

def prune_dict(image, h_dict, build_children_only):
    ''' Returns dependency tree of specified image '''
    for k,v in h_dict.items():
      if(image == k.tree_name or (len(image.split(":")) < 2 and 
          image.split(":")[0] == k.tree_name.split(":")[0]) ):
          if(build_children_only):
              return v
          else:
              return {k : v}
      else:
          dep_tree = prune_dict(image, v, build_children_only)
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

def flatten_hierarchy_dict(h_dict, flat=[]):
    ''' Converts multi-dimensional image dict to image list'''
    for k,v in h_dict.items():
        flat.append(k)
        flatten_hierarchy_dict(v, flat)
    return flat

def add_multi_jar_images(base, jar_data, h_dict):
    ''' Refactor later '''
    n_dict = {}
    if isinstance(h_dict, dict): 
        for image, dep_images in h_dict.items():
            name = lambda x: x.split(":")[0]
            if(base is None or name(base) == name(image.tree_name)):
                for v, jars in jar_data.items():
                    versioned_image = copy.deepcopy(image)
                    versioned_image.tree_name = image.tree_name + "-" + v
                    versioned_image.path = os.path.join(versioned_image.path, v)
                    versioned_image.full_path = os.path.join(versioned_image.path, "image.yaml")
                    versioned_image.multi_version = True
                    versioned_image.kafka_version = v
                    versioned_image.kafka_version_number = v.split("-")[-1]
                    if(base):
                        versioned_image.jar = jars
                    else:
                        versioned_image.parent_image.multi_version = True
                    n_dict.update( { versioned_image : add_multi_jar_images(None, { v : jars }, dep_images) } ) 
            else:
                n_dict.update({ image : add_multi_jar_images(base, jar_data, dep_images) })
    return n_dict

def add_trunk_images(h_dict, config):
    ''' Refactor later '''
    trunks = {}
    for image in h_dict.items():
        if(image[0].base in [trunk.name for trunk in trunks.keys()]):
            for trunk in trunks.keys():
                if(image[0].base == trunk.name):
                  image[0].parent_image = trunk
                  trunks[trunk].update(  { image[0] : image[1]  }  )
        else:
            trunk = Image(".", config)
            trunk.name      = image[0].base
            trunk.tree_name = image[0].base 
            trunk.trunk_image = True
            image[0].parent_image = trunk
            trunks.update( { trunk : { image[0] : image[1]  } } )
      
    return trunks

def create_hierarchy_dict(config):
    ''' Returns hierarchical dictionary '''
    image_list = [] 
   
    # Traverse filesystem, collecting image attributes
    traverse(os.getcwd(), get_images, image_list, config)
 
    image_list = sorted(image_list, key=lambda image:rank(image_list, image.tree_base), reverse=True)

    # Create hierarchical dictionary based on rank
    h_dict = rank_to_hierarchy_dict(image_list)
  
    # Get multi-version image information
    for image, jar_tag in config.jars.items():
        if(jar_tag.multi_version):
            h_dict = add_multi_jar_images(image, jar_tag.combination, h_dict)
 
    h_dict = add_trunk_images(h_dict, config)
    if(config.build_image is not None):
        # Prune dictionary to only specified image tree
        h_dict = prune_dict(config.build_image, h_dict, config.build_children_only)
  
    if(not config.build_children):
        h_dict = dict([ (k,{}) for k,v in h_dict.items() ])

    print_tree(h_dict)

    return h_dict
