import platform
import sys
import shutil
from conan.tools.files import copy, rm
import os
import json

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import buildtool.yabr
from buildhelpers.cmake.aimms_common import copytree
from buildhelpers.gitinfo import gitinfo
     
def deployment(dependencies, graph, output_folder):
    
    for requirement, dependency in dependencies.host.items():
        try:
            
            package_name = dependency.ref.name
            direct = requirement.direct
            
            if direct:
                package_bindir = dependency.cpp_info.bindirs
                package_libdir = dependency.cpp_info.libdirs
                package_dir = dependency.package_folder
                
                if package_bindir == None or len(package_bindir) == 0:
                    continue

                package_bindir = package_bindir[0]
                
                if package_libdir == None or len(package_libdir) == 0:
                    continue
                
                if package_dir is None:
                    continue
                
                package_libdir = package_libdir[0]
                
                print (f"Deploying {package_name}")

                deployer_dir = os.path.join(output_folder, os.getenv('LIBRARYNAME'))
                
                # copy all contents of the package folder to the deployer folder
                copytree(package_dir, deployer_dir)

        except Exception as e:
            print(f"Error deploying {package_name}: {e}")


def deploy(graph, output_folder, **kwargs):
    
    deployment( graph.root.conanfile.dependencies, graph, output_folder)
