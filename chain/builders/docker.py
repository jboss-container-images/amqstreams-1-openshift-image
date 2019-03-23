import threading
import docker
import traceback

from chain.builder import Builder

class DockerBuilder(Builder):
    """Class representing OSBS builder."""

    def __init__(self, config):
        super(type(self), self).__init__(config)
        self.check_prerequistites()
        
    def check_docker_daemon(self):
        try:
          docker_client = docker.from_env()
          if(not docker_client.ping()):
            raise Exception('Failed to connect to docker daemon')
        except Exception as e:
          print(traceback.format_exc())
          raise Exception('Failed to connect to docker daemon')

    def check_prerequistites(self):
      super(type(self), self).check_prerequistites()
      self.check_docker_daemon()
    
    def build(self):
        # For limiting access to shared resources
        lock = threading.Lock()

        print("--- Builds Started ---")
        self.chain_build(self.h_dict, lock)
        print("--- Builds Complete ---")
