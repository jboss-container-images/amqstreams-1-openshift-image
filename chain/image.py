import os
import yaml

class Image():
    def __init__(self, path, config):
        
        self.name          = os.path.basename(os.path.dirname(path))
        self.upstream_name = os.path.basename(os.path.dirname(path))
        self.product_name  = self.get_product_name(self.name)

        self.version       = config.product_version
         
        self.base          = None
        self.product_base  = None        
         
        self.full_path     = path
        self.path          = os.path.dirname(path)
        self.src_path      = os.path.dirname(path)
         
        self.extract_from_idf(path)
         
        self.tree_name     = self.name + ":" + self.version
        self.tree_base     = self.base
        self.rank          = None
        self.parent_image  = None
 
        self.multi_version = False
        self.kafka_version = ""
        self.kafka_version_number = None
        self.jars          = None
        self.trunk_image   = False
        self.log           = os.path.join(config.log_dir, self.name)
        self.log_dir       = config.log_dir
        self.target        = None        
 
    def get_product_name(self, image_name):
        ''' Get from config product line, product '''
        return "amq7/amq-streams-" + image_name

    def extract_from_idf(self, path):
        if(os.path.isfile(path)):
            with open(path, 'r') as yaml_file:
                data = yaml.load(yaml_file, Loader=yaml.FullLoader)
        
            upstream = lambda x: x.replace("amq7/amq-streams-","") 

            self.base         = upstream(data["from"])
            self.product_base = data["from"]

    def extract_from_dockerfile(self):
        return None
