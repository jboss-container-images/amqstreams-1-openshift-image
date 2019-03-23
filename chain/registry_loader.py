import docker

from cekit import tools
from chain.hierarchy import flatten_hierarchy_dict

class RegistryLoader():
    
    def __init__(self, config):
        self.check_prerequistites()
        self.config = config

    def check_docker_daemon(self):
        try:
            docker_client = docker.from_env()
            if(not docker_client.ping()):
                raise Exception('Failed to connect to docker daemon')
        except Exception as e:
            print(traceback.format_exc())
            raise Exception('Failed to connect to docker daemon')

    def check_prerequistites(self):
        self.check_docker_daemon()

    def push_images(self):
        cluster = self.config.cluster
        cluster.authenticate()

        # Log into cotainer registry
        docker_cli = docker.from_env()

        if(docker_cli.login(username=cluster.user, password=cluster.token, registry=cluster.registry)):
            print("docker login -u " + " ".join([cluster.user, "-p", cluster.token, cluster.registry]))
            print("Logged into " + cluster.registry)
        else:
            raise Exception('Failed to login to registry:', cluster.registry)

        f_dict = flatten_hierarchy_dict(self.config.h_dict)
        
        # Create a class for each image
        for image in f_dict:
            if(not image.trunk_image):
                self.push(image, docker_cli, cluster) 
        
    def push(self, image, docker_cli, cluster):
        tagged_images = []
        
        fin  = image.product_name.split(":")[0] # full image name
        tag  = image.tree_name.split(":")[-1]
 
        image_namespace, image_name = fin.split("/")
            
        fin = cluster.registry + "/" + cluster.namespace + "/" + image_name
        
        nn = image.product_name + ":" + tag
        
        if(docker_cli.images.get(nn).tag(fin,tag=tag)):
            tagged_image = [fin + ":" + tag, tag]
            print("Tagged as", tagged_image)
            tagged_images.append(tagged_image)
        else:
            return -1
           
        print("Pushing tagged images to", cluster.registry)
        for image in tagged_images:
          for line in docker_cli.images.push(image[0], stream=True, decode=True):
              print(line)
