import os
import re

def extract_build_info(build):
    ''' Extracts build information from stdout into list'''
    patterns = [
        ["taskID",  '(?<=taskID=)([0-9])*'],
        ["buildID", '(?<=buildID=)([0-9])*'],
        ["image",   '(?<=repositories:\n)(.)*'],
        ["imageTag",'(?<=tags:\s)(.)*(?=,)']
    ]
    with open(build.image.log, 'r') as f:
        text=f.read()

    build_info = []
    for name, regex in patterns:
        matches = re.search(regex, text)
        if( matches is not None ):
            build_info.append(matches.group(0))

    if( build.failure ):
        build_info.append("ERROR")

    return build_info

def log_build(build, lock):
    ''' Write build info to chain build log '''
    build_info = [build.image.tree_name] + extract_build_info(build)

    lock.acquire()
    with open(build.chain_log, 'a') as f:
        form = '%-25s ' + ('%-10s ' * (len(build_info) - 1))
        formatted_output = form % tuple(build_info)
        f.write(formatted_output + "\n")
    lock.release()

def log_build_stdout(text, image):
    ''' Write build stdout to log file '''
    kafka_image = lambda x: "-" + x if x else ""
    log_name= os.path.join(image.log_dir, image.name + kafka_image(image.kafka_version) + ".log")
    image.log = log_name
    with open(image.log, 'a') as f:
      f.write(str(text))
