import os
import subprocess
import distutils.dir_util
import threading

from cekit import tools
from chain.builder import Builder
from chain.hierarchy import flatten_hierarchy_dict

class OSBSBuilder(Builder):
    """Class representing OSBS builder."""

    def __init__(self, config):
        super(type(self), self).__init__(config)
        self.check_prerequistites()
        self.cmd = config.cmd
 
    def build(self):
        # For limiting access to shared resources
        lock = threading.Lock()

        print("--- Builds Started ---")
        self.chain_build(self.h_dict, lock)
        print("--- Builds Complete ---")

        return 0

    """
    ###################################################################### 
    # Pseudocode for commiting all product image source to one dist-git 
    # branch in a single commit. As of right now, this not supported by 
    # infrastructure. Currently we open X commits for X image branches
    ######################################################################
    def generate_source(self):
        ''' Generates and collects cekit source '''
        flatted_hierarchy = flatten_hierarchy_dict(self.h_dict)
        for image in flatted_hierarchy:
          print("Generating ", image)
          self.generate(image)

        return 0
    
    def generate(self, image):
        ''' Generates and collects source for every container image '''
        # Base layer tracking
        cwd = os.path.join(os.getcwd(), image)
        src = os.path.join(cwd, "target", "image")
        des = os.path.join(self.dist_git_dir,  image)
        
        if(os.path.exists(cwd)):
            try:
                process = subprocess.Popen(self.cmd.split(),
                              cwd=cwd,
                              shell=False,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT,
                              stdin=subprocess.PIPE)
                distutils.dir_util.copy_tree(src, des)
        
            except Exception as e:
                print("Error with " + image + " " + e) 
    
    def prepare(self, descriptor):
        # TODO: Load new generic desciptor for bulk commit
        ''' Prepares dist-git repository for OSBS build. '''
        descriptor = tools.load_descriptor(descriptor)

        repository_key = descriptor.get('osbs', {}).get('repository', {})
        repository = repository_key.get('name')
        branch = repository_key.get('branch')

        if not (repository and branch):
            raise CekitError(
                "OSBS builder needs repostiory and branch provided!")

        if self._stage:
            osbs_dir = 'osbs-stage'
        else:
            osbs_dir = 'osbs'

        self.dist_git_dir = os.path.join(os.path.expanduser(config.get('common', 'work_dir')),
                                         osbs_dir,
                                         repository)
        if not os.path.exists(os.path.dirname(self.dist_git_dir)):
            os.makedirs(os.path.dirname(self.dist_git_dir))

        self.dist_git = DistGit(self.dist_git_dir,
                                self.target,
                                repository,
                                branch)
    
    def commit(self):
        ''' Commit image sources to dist-git '''
        self.generate_source()
        print("commiting source")
        # Get git repo from CONFIG file
        
        with Chdir(self.dist_git_dir):
            self.dist_git.add()
            # May need to update this
            self.update_lookaside_cache()

            if self.dist_git.stage_modified():
                self.dist_git.commit(self._commit_msg)
                self.dist_git.push()
            else:
                logger.info("No changes made to the code, committing skipped")
    
    def update_lookaside_cache(self):
        # Might need to update this
        logger.info("Updating lookaside cache...")
        if not self.artifacts:
            return
        cmd = [self._rhpkg]
        if self._user:
            cmd += ['--user', self._user]
        cmd += ["new-sources"] + self.artifacts

        print(cmd)
        logger.debug("Executing '%s'" % cmd)
        with Chdir(self.dist_git_dir):
            try:
                subprocess.check_output(cmd, stderr=subprocess.STDOUT)
                except subprocess.CalledProcessError as ex:
                    logger.error("Cannot run '%s', ouput: '%s'" % (cmd, ex.output))
                    raise CekitError("Cannot update sources.")
        
        logger.info("Update finished.")
    """
