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

def get_webui_runtime_version():
    if os.getenv("CI", "false") == "true":
        gi = gitinfo("webui/frontend")
        version = gi.getVersion()
    else:
        try:
            with open("repository_library_release.json") as f:
                data = json.load(f)
                version = data["local_webui_runtime"]
        except Exception as e:
            print(e)
    
    return version
     
def deployment(dependencies, graph, output_folder):
    
    skip_list = ["log4cxx", "eventbus", "common", "armi4cxx", "net4cxx", "net4cxx-dev", "crt", "servicelocator", "beastweb", "openssl", "atp4cxx"]
    
    for requirement, dependency in dependencies.host.items():
        try:
            
            package_name = dependency.ref.name
            
            if package_name in skip_list:
                continue
            
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

            deployer_dir = os.path.join(output_folder)
            
            # get a webui_runtime version locally for testing purposes
            if package_name == "webui_runtime" and os.getenv("CI", "false") == "false":
                copy(graph.root.conanfile, "*", os.path.join(package_dir), os.path.join(deployer_dir, "..", "webui"))
            else:
                
                copy(graph.root.conanfile, "*.dll", package_bindir, deployer_dir)
                copy(graph.root.conanfile, "*.so*", package_bindir, deployer_dir)
                copy(graph.root.conanfile, "*.so*", package_libdir, deployer_dir)
                
                is_ci = os.getenv("CI", "false") == "true"
                
                if (platform.system() == "Windows"):
                    copy(graph.root.conanfile, "*.pdb*", package_bindir, deployer_dir)
                    
                if (platform.system() == "Linux"):
                    copy(graph.root.conanfile, "*.debug*", package_bindir, deployer_dir)
                    copy(graph.root.conanfile, "*.debug*", package_libdir, deployer_dir)
                
            # deployment(dependency.dependencies, graph, output_folder)
        except KeyError:
            print(f"Skipping {requirement} as it is not a conan package")

'''

This is the function that conan will call when the deploy generator is used with command
conan install installer/conanfile.py 
--deployer=aimms_deploy 
-pr:h buildhelpers/conan-profiles/windows/x86_64/vc143/RelWithDebInfo 
-pr:b buildhelpers/conan-profiles/windows/x86_64/vc143/RelWithDebInfo 
--deployer-folder E:/git/aimms/out -of out/conan_output

'''
def deploy(graph, output_folder, **kwargs):
    
    deployment( graph.root.conanfile.dependencies, graph, output_folder)

    src_dir = os.path.join(os.getcwd(), "webui", "perf-init")
    boomerang_path = os.path.join(src_dir, "boomerang.js")
    tti_path = os.path.join(src_dir, "tti.js")
    dst_dir = os.path.join(output_folder, output_folder)
    shutil.copy(boomerang_path, dst_dir)
    shutil.copy(tti_path, dst_dir)
