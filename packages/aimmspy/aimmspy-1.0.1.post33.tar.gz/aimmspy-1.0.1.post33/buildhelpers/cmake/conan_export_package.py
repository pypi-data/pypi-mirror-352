import platform
import subprocess
import json
import sys
import os
import logging
import tempfile
from conan_signtool import signBinaries
from aimms_common import executeCmd, repo_dirty
from aimms_artifactory import quit_job_if_on_artifactory

log = logging.basicConfig(level=logging.INFO)

def get_fully_qualified_package_name(file_name):
    with open(file_name, 'r') as json_file:
        data = json.load(json_file)

    return data["graph"]["nodes"]['0']["ref"].split("#")[0]

def sign_binaries(file_name):
    with open(file_name, 'r') as json_file:
        data = json.load(json_file)

    package_data = data["graph"]["nodes"]['0']

    _settings = package_data["settings"]
    if "os" in _settings:
        _os = _settings["os"]
        _build_type = "Release" if "build_type" not in _settings else _settings["build_type"]

        if _os == "Windows" and (_build_type == "Release" or _build_type == "RelWithDebInfo"):
            signBinaries(os.path.join(package_data["package_folder"], "bin"))
            signBinaries(os.path.join(package_data["package_folder"], "lib"))

if __name__ == '__main__':
    working_folder = os.getenv('CHANGE_FOLDER')
    package_user = os.getenv('PACKAGE_USER')
    package_channel = os.getenv('PACKAGE_CHANNEL')
    profile_dir = os.getenv('PROFILES_DIR')
    profile_host = os.getenv('profile_host')
    profile_build = os.getenv('profile_build')
    preset = os.getenv('preset')
    build_type = os.getenv('build_type' , "")
    version = os.getenv('version', "")
    name = os.getenv('name', "")
    
    if version:
        version = f"--version {version}"

    if name:
        name = f"--name {name}"

    # get operating system
    os_name = platform.system()

    tempdir = tempfile._get_default_tempdir()
    export_pkg_json = f"{tempdir}/export-pkg.json"
    repo_dirty(throw=False)
    
    # user channel cannot contain capital letters check for this and throw error
    if package_user.islower() == False:
        raise ValueError("package_user cannot contain capital letters please change this to lowercase")
    if package_channel.islower() == False:
        raise ValueError("package_channel cannot contain capital letters please change this to lowercase")
    
    print (f"preset: {preset}")

    profile_host = f"{profile_dir}/{profile_host}"
    profile_build = f"{profile_dir}/{profile_build}"
    
    if preset and "@" in preset:
        compiler, arch = preset.split("@")
        
        profile_host = f"{profile_dir}/{os_name.lower()}/{arch}/{compiler}/{build_type}"
        profile_build = f"{profile_dir}/{os_name.lower()}/{arch}/{compiler}/build"
    
    executeCmd(f"conan export-pkg {working_folder}/conanfile.py -vtrace --user {package_user} --channel {package_channel} -pr:b {profile_build} -pr:h {profile_host} {version} {name} -f json > {export_pkg_json}")
    
    full_qualified_package_name = get_fully_qualified_package_name(export_pkg_json)
    name_and_version = full_qualified_package_name.split("@")[0]
    name, version = name_and_version.split("/")
    quit_job_if_on_artifactory(name, version, package_channel, preset, build_type, os_name)

    repo_dirty(throw=False)
    sign_binaries(export_pkg_json)

    # if full_qualified_package_name is larger than 200 throw error
    if len(full_qualified_package_name) > 200:
        raise ValueError("package ref cannot be larger than 200 characters please change this to a shorter name")
    
    
    executeCmd(f"conan upload -vtrace {full_qualified_package_name} -r conan-intra")
    repo_dirty(throw=False)
