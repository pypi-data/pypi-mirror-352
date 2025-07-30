import argparse
import json
import os
import os.path
import shutil
import subprocess
import typing
import uuid
import xml.etree.ElementTree as et

from jl95terceira.pytools import maven
from jl95terceira.batteries import *

DEFAULT_DEST_RELATIVE = 'target'

def do_it(pom_path:str,
          dest:str):
    
    os.makedirs(dest, exist_ok=True)
    pom = maven.Pom(pom_path)
    for dep in pom.dependencies():

        shutil.copy(maven.get_local_jar_path(dep), dest)

if __name__ == '__main__':

    p = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                description='Download and build Maven dependencies from their corresponding Github projects')
    class A:
        PROJECT_DIR  = 'wd'
        DESTINATION_DIR = 'dest'
    p.add_argument(f'--{A.PROJECT_DIR}',
                   help=f'Project / working dir\nDefault: current directory')
    p.add_argument(f'--{A.DESTINATION_DIR}',
                   help=f'Directory to which to copy the dependencies (Java jar files)\nIf omitted, it is assumed as {DEFAULT_DEST_RELATIVE} under the project directory.')
    # parse args
    get = p.parse_args().__getattribute__
    proj_dir    = get(A.PROJECT_DIR) if get(A.PROJECT_DIR) is not None else os.getcwd()
    pom_path    = maven.get_pom_path_by_project_dir(proj_dir)
    target_path = get(A.DESTINATION_DIR) if get(A.DESTINATION_DIR) is not None else os.path.join(proj_dir, DEFAULT_DEST_RELATIVE)
    # do it
    do_it(pom_path,
          target_path)
