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
    lock:       mutex for resources shared among builds (e.g. dist-git repo)
  """
  def __init__(self, image, cmd, lock):
    self.image = image
    self.cmd = cmd
    self.lock = lock
    self.failure = None
    threading.Thread.__init__(self)

  def run(self):
    stdout=""
    cwd = os.path.join(os.getcwd(), self.image)
    if(os.path.exists(cwd)):
      self.thread_safe_print("Building %s ..." % self.image)
      try:
        self.lock.acquire()
        self.log_build(self.cmd + "\n")
        process = subprocess.Popen(self.cmd.split(),
                           cwd=cwd,
                           shell=False,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT,
                           stdin=subprocess.PIPE)

        self.commit_and_kick(process)
        self.lock.release()

        stdout, err  = process.communicate()
        self.failure = process.returncode
        self.log_build(stdout)
        if(not self.failure):
          self.thread_safe_print("Completed " + self.image)
      except Exception as e:
        self.log_build(stdout + traceback.format_exc())
        self.lock.release()
        self.failure = process.returncode
        self.thread_safe_print("Incomplete " + self.image)

  def commit_and_kick(self, process):
    ''' Commits code to dist-git and kicks OSBS build '''
    if("osbs" in self.cmd):
      text = ""
      while( process.poll() is None ):
        output = process.stdout.readline()
        text += output
        # If prompted, answer yes
        process.stdin.write(b'Y\n')
        if("Created task" in output):
          break
      self.log_build(text)
 
  def thread_safe_print(self, str):
    ''' Allow only one thread to write to stdout at a time'''
    self.lock.acquire()
    print(str)
    self.lock.release()

  def log_build(self, text):
    ''' Write build stdout to log file '''
    logs_dir="logs"
    if not os.path.exists(logs_dir):
      os.makedirs(logs_dir)
    log_file = os.path.join(logs_dir, self.image + ".log")
    with open(log_file, 'a') as f:
      f.write(str(text))
