import platform
import shutil
import sys
from conan.tools.files import copy, rm
import os

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cmake'))
from aimms_common import copytree
     
def deployment(dependencies, graph, output_folder):
    for requirement, dependency in dependencies.host.items():
        try:
            
            package_name = dependency.ref.name
            
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
        
            if package_name == "solvers" or "External Solver" in dependency.description:
                # this is for the ac team to not deploy solvers if they are actively working on them
                if not os.environ.get('SOLVER_DEPLOYMENT_SKIP_FOR_AC'):
                    deployer_dir = os.path.join(output_folder, "Solvers")
                    solvers_dir = os.path.join(package_dir, "solvers")
                    copy(graph.root.conanfile, "*", solvers_dir, deployer_dir)
                    copy(graph.root.conanfile, "*", package_libdir, deployer_dir)
                    
                    # remove all static libs .lib and .a files
                    rm(graph.root.conanfile, "*.a", deployer_dir)
                    rm(graph.root.conanfile, "*.lib", deployer_dir)
                    rm(graph.root.conanfile, "*.exp", deployer_dir)
                
            elif package_name == "aimms":
                deployer_dir = os.path.join(output_folder, "Bin")
                copy(graph.root.conanfile, "*", package_bindir, deployer_dir)    
              
            else:
                deployer_dir = os.path.join(output_folder, "Bin")
                copy(graph.root.conanfile, "*.dll", package_bindir, deployer_dir)
                copy(graph.root.conanfile, "*.pdb", package_bindir, deployer_dir)
                copy(graph.root.conanfile, "*.so*", package_bindir, deployer_dir)
                copy(graph.root.conanfile, "*.so*", package_libdir, deployer_dir)
                # also get linux .debug files
                copy(graph.root.conanfile, "*.debug", package_bindir, deployer_dir)
                copy(graph.root.conanfile, "*.debug", package_libdir, deployer_dir)
                
                # make sure include dir array is not empty
                if len(dependency.cpp_info.includedirs) != 0:
                    copy(graph.root.conanfile, "olch2xu8.ocx", dependency.cpp_info.includedirs[0], deployer_dir)
                    copy(graph.root.conanfile, "olch3xu8.ocx", dependency.cpp_info.includedirs[0], deployer_dir)
                    
                    copy(graph.root.conanfile, "olch2xu8.ocx.manifest", dependency.cpp_info.includedirs[0], deployer_dir)
                    copy(graph.root.conanfile, "olch3xu8.ocx.manifest", dependency.cpp_info.includedirs[0], deployer_dir)
                
                # copy aimms.exe AimmsCmd.exe AimmsCOM.exe CompLis.exe node.exe OpenPDFtopic.exe StgConv.exe
                copy(graph.root.conanfile, "aimms.exe", package_bindir, deployer_dir)
                copy(graph.root.conanfile, "AimmsCmd.exe", package_bindir, deployer_dir)
                copy(graph.root.conanfile, "AimmsCOM.exe", package_bindir, deployer_dir)
                copy(graph.root.conanfile, "CompLis.exe", package_bindir, deployer_dir)
                copy(graph.root.conanfile, "FakeNode.exe", package_bindir, deployer_dir)
                copy(graph.root.conanfile, "OpenPDFtopic.exe", package_bindir, deployer_dir)
                copy(graph.root.conanfile, "StgConv.exe", package_bindir, deployer_dir)
                
                if platform.system() == "Linux":
                    copy(graph.root.conanfile, "DriveID", package_bindir, deployer_dir)
                    copy(graph.root.conanfile, "NodelockTool", package_bindir, deployer_dir)
                    copy(graph.root.conanfile, "FakeNode", package_bindir, deployer_dir)
 
            if os.path.exists(os.path.join(package_dir, "ifa_files")):
                copytree(os.path.join(package_dir, "ifa_files"), os.path.join(output_folder), ignore=True)
                
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
def modifications(output_folder):
    if platform.system() == "Linux" and os.path.exists(os.path.join(os.path.join(output_folder, "Bin"), "FakeNode")):
        shutil.move(os.path.join(os.path.join(output_folder, "Bin"), "FakeNode"), os.path.join(os.path.join(output_folder, "Bin"), "node"))
                    
    if platform.system() == "Windows" and os.path.exists(os.path.join(os.path.join(output_folder, "Bin"), "FakeNode.exe")):
        shutil.move(os.path.join(os.path.join(output_folder, "Bin"), "FakeNode.exe"), os.path.join(os.path.join(output_folder, "Bin"), "node.exe"))


def deploy(graph, output_folder, **kwargs):
    
    deployment( graph.root.conanfile.dependencies, graph, output_folder)
    
    modifications(output_folder)
