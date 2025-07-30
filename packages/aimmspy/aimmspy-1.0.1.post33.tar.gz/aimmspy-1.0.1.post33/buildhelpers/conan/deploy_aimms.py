import sys
import os

sys.path.append(os.path.join(os.getcwd()))
sys.path.append(os.path.join(os.getcwd(), "buildhelpers"))
sys.path.append(os.path.join(os.getcwd(), "buildhelpers", "conan"))
sys.path.append(os.path.join(os.getcwd(), "buildhelpers", "cmake"))

import cmake.aimms_artifactory as aimms_artifactory
import subprocess
import platform
import shutil

def deploy_aimms(cmake_preset: str, branch: str, cmake_build_type: str, version: str = "latest", version_or_latest: bool = False):


    # if env variable AIMMS_FOLDER_DEPLOY_VERSION_NAME is set, use that as the version
    if os.getenv("AIMMS_FOLDER_DEPLOY_VERSION_NAME"):
        folder_version = os.getenv("AIMMS_FOLDER_DEPLOY_VERSION_NAME")
        aimms_folder = os.path.join(os.getcwd(), 'aimms', folder_version, cmake_build_type)
        if os.path.exists(aimms_folder):
            with open(os.path.join(aimms_folder, 'Bin', 'SuiteVersion.txt'), 'r') as file:
                version_from_file = file.read().strip()
                print(f"Version from AIMMS_FOLDER_DEPLOY_VERSION_NAME: {version}")
            
            if version == version_from_file:
                print(f"Aimms folder {aimms_folder} already exists")
                return version
            else:
                print(f"Version from AIMMS_FOLDER_DEPLOY_VERSION_NAME: {version_from_file} does not match the version provided: {version}")
                print(f"Deleting the folder {aimms_folder}")
                shutil.rmtree(aimms_folder)
                
    else:
        folder_version = version
        aimms_folder = os.path.join(os.getcwd(), 'aimms', folder_version, cmake_build_type)
        if os.path.exists(aimms_folder):
            print(f"Aimms folder {aimms_folder} already exists")
            return version

    compiler = cmake_preset.split('@')[0]
    arch = cmake_preset.split('@')[1]

    profile_path = os.path.join(os.getcwd(), 'buildhelpers', 'conan-profiles', platform.system().lower(), arch, compiler, cmake_build_type)
    conanfile_path = os.path.join(os.getcwd(), 'buildhelpers', 'autolibs', 'get_aimms.py')
    aimms_deployer_path = os.path.join(os.getcwd(), 'buildhelpers', 'aimms_deploy.py')
    conan_garbage_path = os.path.join(os.getcwd(), 'out', 'conan_output')

    aimms_deploy_location = os.path.join(os.getcwd(), 'aimms', folder_version, cmake_build_type)
    conan_command = ["conan", "install", conanfile_path, "--deployer", aimms_deployer_path, "-pr:b", profile_path, "-pr:h", profile_path, "--deployer-folder", aimms_deploy_location, "-of", conan_garbage_path]

    print(f"Running conan install command: {conan_command}")
    print(f"Current working directory: {os.getcwd()}")

    if version == "latest":
        version = str(aimms_artifactory.get_latest_version_artifactory(
            "aimms", branch))

    # get environment variables
    env = os.environ.copy()
    env['AIMMS_TEST_BRANCH'] = branch
    env['AIMMS_TEST_VERSION'] = version

    process0 = subprocess.run(conan_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)

    print( process0.stdout.decode())

    if process0.returncode != 0:
        print( f"Conan install command failed with error: {process0.stderr.decode()}")
        if version_or_latest:
            
            version = str(aimms_artifactory.get_latest_version_artifactory("aimms", branch))
            env['AIMMS_TEST_VERSION'] = version
            print(f"Trying to install latest version of AIMMS")
            
            if os.getenv("AIMMS_FOLDER_DEPLOY_VERSION_NAME"):
                folder_version = os.getenv("AIMMS_FOLDER_DEPLOY_VERSION_NAME")
            else:
                folder_version = version
            
            aimms_deploy_location = os.path.join(os.getcwd(), 'aimms', folder_version, cmake_build_type)
            conan_command = ["conan", "install", conanfile_path, "--deployer", aimms_deployer_path, "-pr:b", profile_path, "-pr:h", profile_path, "--deployer-folder", aimms_deploy_location, "-of", conan_garbage_path]
            
            print (f"Running conan install command: {conan_command}")
            process1 = subprocess.run(conan_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
            print( process1.stdout.decode())
            if process1.returncode != 0:
                print ( f"Conan install command failed with error: {process1.stderr.decode()}")
                
        else:
            print(
                f"Conan install command failed with error: {process0.stderr.decode()}")

    aimms_folder = os.path.join(os.getcwd(), 'aimms', folder_version, cmake_build_type)
    if not os.path.exists(aimms_folder):
        exit(f"Aimms folder {aimms_folder} does not exist")
    
    return version
