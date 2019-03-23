import os

from chain.image import Image

def get_images(path, image_list, config):
  ''' Appends directories containing image descriptor files to list '''
  dirname = os.path.basename(os.path.dirname(path)) 
  if(os.path.basename(path) == 'image.yaml' and 'image.yaml' not in 
                  os.listdir(os.path.dirname(os.path.dirname(path)))):
      image = Image(path, config) 
      image_list.append(image)
 
      return True
  return False

def traverse(path, function, *args):
  ''' Recursively traverses path, applying function to all files '''
  if(function(path, *args) or os.path.isfile(path) or os.path.basename(path) == 'target' ):
    return 0
  files = [os.path.join(path, f) for f in os.listdir(path)]
  for f in files:
    traverse(f, function, *args)
