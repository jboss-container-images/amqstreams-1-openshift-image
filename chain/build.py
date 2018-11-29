import os
import subprocess
import threading
import time
import traceback

class Build(threading.Thread):
  """ 
  Thread object which executes and tracks a forked process. 
  Used for building container images concurrently
    
  Args:
    image:      image to build
    cmd:        command to run in every image directory
    parent:     parent build process that current build is dependent on
    lock:       mutex for resources shared among builds (e.g. dist-git repo)
  """
  def __init__(self, image, cmd, parent, lock):
    self.image = image
    self.cmd = cmd
    self.stdout = ''
    self.stderr = ''
    self.process = None
    self.parent = parent
    self.lock = lock
    threading.Thread.__init__(self)

  def run(self):

    if(self.parent != None): 
      # Block until parent build has completed
      #self.thread_safe_print("wait")
      self.parent.join()
      #self.thread_safe_print("unwait")

    cwd = os.path.join(os.getcwd(), self.image)
    if(os.path.exists(cwd)):
      self.thread_safe_print("Building %s ..." % self.image)
      try:
        self.lock.acquire()
        self.log(self.cmd + "\n")
        self.process = subprocess.Popen(self.cmd.split(),
                           cwd=cwd,
                           shell=False,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT,
                           stdin=subprocess.PIPE)

        self.commit_and_kick()
        self.lock.release()

        self.stdout, self.stderr = self.process.communicate()
        self.log(self.stdout)
        self.thread_safe_print("Completed " + self.image)
      except Exception as e:
        self.log(self.stdout + traceback.format_exc())
        self.lock.release()
        self.thread_safe_print("Incompleted " + self.image) 

  def commit_and_kick(self):
    ''' Commits code to dist-git and kicks OSBS build '''
    if("osbs" in self.cmd):
      text = ""
      while( self.process.poll() is None ):
        output = self.process.stdout.readline()
        text += output
        # If prompted, answer yes
        self.process.stdin.write(b'Y\n')
        if("Created task" in output):
          break
      self.log(text)
 
  def thread_safe_print(self, str):
    ''' Allow only one thread to write to stdout at a time'''
    self.lock.acquire()
    print(str)
    self.lock.release()

  def log(self, text):
    ''' Write build stdout to log file '''
    logs_dir="logs"
    if not os.path.exists(logs_dir):
      os.makedirs(logs_dir)
    log_file = os.path.join(logs_dir, self.image + ".log")
    with open(log_file, 'a') as f:
      f.write(str(text))
