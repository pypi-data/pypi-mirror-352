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
from jl95terceira.pytools.envlib.vars.git  import GIT
from jl95terceira.pytools.envlib.vars.java import MAVEN
from jl95terceira.batteries import *

DEPS_MAPFILE_NAME_STANDARD = 'depsmap.json'

class DepInfo:

    def __init__(self,x):

        self.url    :str = x['url']
        self.version:typing.Callable[[str],str] \
                         = eval(x['version']) if 'version' in x else lambda vn: f'v{vn}'

class DepsInstaller:

    def __init__(self, project_dir:str):

        self._pom = maven.Pom.from_project_dir(project_dir if project_dir is not None else os.getcwd())

    def install_deps_by_map(self, deps_map:dict[tuple[str,str],dict[str,typing.Any]]):

        for dep in self._pom.dependencies():

            if maven.is_installed(dep): # already installed
                
                continue

            dep_key = (dep.group_id,dep.artifact_id)
            if dep_key not in deps_map: # not to look up
                
                continue

            dep_info = DepInfo(deps_map[dep_key])
            temp_dir_name = f'_dep-{dep.group_id}-{dep.artifact_id}-{str(uuid.uuid4())}'
            git = GIT  .get()
            mvn = MAVEN.get()
            os.makedirs(temp_dir_name)
            try:
                subprocess.run([git,'clone',dep_info.url,temp_dir_name,'--branch',dep_info.version(dep.version),'--depth','1'],
                            shell=True)
                wd = os.getcwd()
                os.chdir(temp_dir_name)
                try:
                    subprocess.run([mvn,'install','-Dmaven.test.skip=true'],
                                   shell=True)
                    if DEPS_MAPFILE_NAME_STANDARD in os.listdir():

                        DepsInstaller(os.getcwd()).install_deps()

                finally:
                    os.chdir(wd)
            finally:
                subprocess.run([git,'clean','-ff',temp_dir_name],shell=True)

    def install_deps_by_mapfile_path(self, deps_mapfile_path:str):

        with open(deps_mapfile_path, mode='r') as fr:

            deps_map_raw:dict[str,typing.Any] = json.load(fr)
            deps_map = dict((tuple(k.split(':')[:2]),v) for k,v in deps_map_raw.items())

        self.install_deps_by_map(deps_map)

    def install_deps(self, project_dir:str):

        self.install_deps_by_mapfile_path(os.path.join(project_dir, DEPS_MAPFILE_NAME_STANDARD))

if __name__ == '__main__':

    p = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                description='Download and build Maven dependencies from their corresponding Github projects')
    class A:
        DEPS_MAPFILE = 'mapfile'
        PROJECT_DIR  = 'wd'
    class Defaults:
        DEPS_MAPFILE = DEPS_MAPFILE_NAME_STANDARD
    p.add_argument(f'--{A.PROJECT_DIR}',
                   help=f'Project / working dir\nDefault: current directory')
    p.add_argument(f'--{A.DEPS_MAPFILE}',
                   help=f'Path of dependencies map file to consider, relative to working directory, if different from the standard ({Defaults.DEPS_MAPFILE})',
                   default=Defaults.DEPS_MAPFILE)
    # parse
    get = p.parse_args().__getattribute__
    project_dir       = get(A.PROJECT_DIR)
    deps_mapfile_path = get(A.DEPS_MAPFILE)
    # do it
    DepsInstaller(project_dir).install_deps_by_mapfile_path(deps_mapfile_path=deps_mapfile_path)
