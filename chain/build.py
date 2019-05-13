import os
import subprocess
import threading
import time
import traceback

from chain.logging import log_build_stdout

class Build(threading.Thread):
  """ 
  Thread object which executes and tracks a forked process. 
  Used for building container images concurrently
    
  Args:
    image:      image to build
    cmd:        command to run in every image directory
    lock:       mutex for resources shared among builds (e.g. dist-git repo)
  """
  def __init__(self, image, config, lock):
    self.image       = image
    self.config      = config 
    self.log         = image.log
    self.chain_log   = config.log 
    self.lock        = lock
    self.failure     = None
     
    threading.Thread.__init__(self)

  def run(self):
    stdout=""
    cwd = self.image.path
    if(self.config.build_type == "release" or self.config.build_type == "scratch"):
        self.config.cmd = self.config.cmd + " --build-osbs-target " + "rh-amqstreams-1.1-rhel-7-containers-candidate" #self.image.target
        #print(self.config.cmd)
    if(os.path.exists(cwd)):
      self.thread_safe_print("Building %s ..." % self.image.tree_name)
      try:
        self.lock.acquire()
        log_build_stdout(self.config.cmd + "\n", self.image)
        process = subprocess.Popen(self.config.cmd.split(),
                           cwd=cwd,
                           shell=False,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT,
                           stdin=subprocess.PIPE,
                           universal_newlines=True)

        self.commit_and_kick(process)
        self.lock.release()

        stdout, err  = process.communicate()
        self.failure = process.returncode
        log_build_stdout(stdout, self.image)
        if(not self.failure):
          self.thread_safe_print("Completed " + self.image.tree_name)
      except Exception as e:
        log_build_stdout(stdout + traceback.format_exc(), self.image)
        self.lock.release()
        self.failure = process.returncode
        self.thread_safe_print("Incomplete " + self.image.tree_name)

  def commit_and_kick(self, process):
    ''' Commits code to dist-git and kicks OSBS build '''
    if(self.config.osbs_build):
      text = ""
      while( process.poll() is None ):
        output = process.stdout.readline()
        text += output
        # If prompted, answer yes
        process.stdin.write('Y\n')
        process.stdin.flush()
        if("Created task" in output):
          break
      log_build_stdout(text, self.image)
 
  def thread_safe_print(self, str):
    ''' Allow only one thread to write to stdout at a time '''
    self.lock.acquire()
    print(str)
    self.lock.release()
