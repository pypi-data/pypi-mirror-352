import argparse
import os
import sys
import platform

sys.path.append(os.path.join(os.getcwd(), "buildhelpers", "cmake"))
import linux_debug_info_d

# set the path to the buildhelpers folder
from aimms_common import get_alib_name, get_build_types, executeCmd, get_correct_toolset
from conan_signtool import signBinaries

# set the path to the buildhelpers folder
sys.path.append(os.path.join(os.getcwd()))
import buildhelpers.gitinfo as gitinfo
import buildtool.generalBuildSupport as gbs
from buildtool.LibraryRepository import libraryRepo
import json
import datetime

'''
{
    "libraries": [
        {
            "name": "AimmsUnitTest",
            "uuid": "7A2E765C-2A09-4456-8583-C7AF9DE0484D",
            "description": "A unit testing framework for AIMMS projects.",
            "tag": "unit test, testing",
            "dependency": [],
            "release_note_page": "https://documentation.aimms.com/unit-test/release.html"
        }
    ]
}
'''
class library_info:
    def __init__(self, name, uuid, description, tag, dependencies, release_note_pages, ams_file, deploy_file, is_sfx):
        self.name = name
        self.uuid = uuid
        self.description = description
        self.tag = tag
        self.dependencies = dependencies
        self.release_note_pages = release_note_pages
        self.ams_file = ams_file
        self.deploy_file = deploy_file
        self.is_sfx = is_sfx
        self.minveraimms = None  # optional, str like "24.x.y.z"
        self.pureaimms = False    # optional
        self.force_release = None # optional, str is version of an official release from a "non releasable" branch [CAREFUL!!!]


    def __str__(self):
        # check if we have optional values
        mva="" if not isinstance(self.minveraimms,str) else f"""
    MinverAimms:
    {self.minveraimms}    
    """

        fr="" if not isinstance(self.force_release,str) else f"""
    FORCED RELEASE VERSION:
    {self.force_release}    
    """    
        # return everything, optionals at the end        
        return f"""
    Name:
    {self.name}
    
    UUID:
    {self.uuid}

    Description:
    {self.description}

    Tag:
    {self.tag}

    Dependencies:
    {self.dependencies}

    Release Note Pages:
    {self.release_note_pages}

    Deploy File:
    {self.deploy_file}
    {mva}{fr}
    
    SFX:
    {self.is_sfx}
    """

# parse a json file with the above structure to get the libraries, uuids, descriptions, tags, dependencies and release notes
class repository_library_release_info:
    def __init__(self, json_file_path):
        # open JSON file if string
        if isinstance(json_file_path, str):
            with open(json_file_path) as json_file:
                data = json.load(json_file)
        else: # assume json_file_path is already a correct dict
            data = dict()
            data["libraries"]=json_file_path 

        self.force_release=None
        self.libraries = []
        for library in data["libraries"]:
            deploy_file = "autolib_deploy.py"
            if "custom_deploy" in library and library["custom_deploy"] != "":
                deploy_file = library["custom_deploy"]

            is_sfx = True if "is_sfx" in library and library["is_sfx"] else False
            libinfo = library_info(library["name"], library["uuid"], library["description"], library["tag"], library["dependency"], library["release_note_page"], library["ams_file"], deploy_file, is_sfx)
                
            if "minveraimms" in library:
                libinfo.minveraimms = library["minveraimms"]
            if "pureaimms" in library:
                libinfo.pureaimms = library["pureaimms"]
            if "forcerelease" in library:       
                libinfo.force_release = library["forcerelease"]
                self.force_release = libinfo.force_release # take last value as true

            self.libraries.append(libinfo)    

        system = platform.system().lower()
        self.is_windows = system == 'windows'
        self.is_linux = system == 'linux'
        self.is_mac = system == 'darwin'

        self.author = "AIMMS B.V."
        self.copyright = 'Copyright (c) 2017-{} AIMMS B.V. All rights reserved.'.format(datetime.date.today().year)

        semver_version = gitinfo.gitinfo().getVersion()
        self.project_version = semver_version.replace("-", ".")
        self.branch_type = gitinfo.gitinfo().getBranchType()

        self.branch = os.getenv("CI_COMMIT_REF_NAME", "None")
        
    def __str__(self):
        string_repersentation = "Libraries:\n"

        for library in self.libraries:
            string_repersentation += "    ======================================================================================\n"
            string_repersentation += str(library)
            string_repersentation += "======================================================================================\n"
            
        string_repersentation += f"""
    Platform:
    - Windows: {self.is_windows}
    - Linux: {self.is_linux}
    - macOS: {self.is_mac}

    Author: {self.author}
    Project Version: {self.project_version}
    Branch Type: {self.branch_type}
    Branch: {self.branch}
    """

        return string_repersentation

def is_pipeline():
    return os.getenv("CI", "false") == "true"

def signAutoLib(path, cmake_build_config):
    # try to get env var CI to see if we are in a CI environment
    if (cmake_build_config == "Release" or cmake_build_config == "RelWithDebInfo")  and platform.system() == "Windows" and is_pipeline():
        print ("           Signing binaries")
        signBinaries(path)

def deploy_binaries(library_info, cmake_configuration, cmake_build_config):
    cmake_label, cmake_arch = cmake_configuration.split("@")

    print(f"""
===============================================
    EXECUTING CONAN INSTALL AND DEPLOY SCRIPT FOR {library_info.name.upper()} {str(cmake_configuration).upper()} {str(cmake_build_config).upper()}
    
    This script installs dependencies using Conan and deploys them using a custom deployer script in                         
    buildhelper/autolibs/autolib_deploy
    
    We need this because the binaries in conan need to be in the same folder as the DLLs of the build autolib.

===============================================
""")
    
    deploy_folder = os.path.join(os.getcwd(), "out", "upload", cmake_configuration, cmake_build_config, library_info.name)
    if not library_info.is_sfx:
        deploy_folder = os.path.join(deploy_folder, "DLL")

    executeCmd(
        f"conan install . --deployer=buildhelpers/autolibs/{library_info.deploy_file} "
        f"-pr:h buildhelpers/conan-profiles/{platform.system().lower()}/{cmake_arch}/{cmake_label}/{cmake_build_config} "
        f"-pr:b buildhelpers/conan-profiles/{platform.system().lower()}/{cmake_arch}/{cmake_label}/build "
        f"--deployer-folder {deploy_folder} -of out/conan_output",
        silent=True
    )

def createSfx(cmake_configuration, cmake_build_config, library_info, version):
    compiler, arch = cmake_configuration.split("@")
    autolibToolset = f"{compiler}_{arch}_{cmake_build_config}"
    
    src = os.path.join(os.getcwd(), "out", "upload", cmake_configuration, cmake_build_config, library_info.name)
    dst = os.path.join(os.getcwd(), "out", "upload", cmake_configuration, "bin")

    gbs.createSfx(src, dst, version, library_info.name, autolibToolset, "", "")
    
    # 7z files are intermediate files used to create the self extracting executable.
    # We don't need them anymore so we delete them, since everything in the destination folder is later uploaded to the library repository
    for file in os.listdir(dst):
        if file.endswith(".7z"):
            os.remove(os.path.join(dst, file))

    signAutoLib(dst, cmake_build_config)

def createlib(cmake_configuration, cmake_build_config, library_info, version):
    # assume cmake build and copied everything to the right spot
    # we then only have to create a lib for uploading
    
    compiler, arch = cmake_configuration.split("@")

    autolibToolset = get_alib_name(compiler, arch, cmake_build_config)
    autolibToolset = os.path.splitext(autolibToolset)[0]

    # echo the command to the console
    # print(f"conan install . --deployer=buildhelpers/autolibs/autolib_deploy.py -pr:h buildhelpers/conan-profiles/{platform.system().lower()}/{cmake_arch}/{cmake_label}/{cmake_build_config} -pr:b buildhelpers/conan-profiles/{platform.system().lower()}/{cmake_arch}/{cmake_label}/{cmake_build_config} --deployer-folder out/upload/{cmake_configuration}/{cmake_build_config}/autolib/DLL -of out/conan_output")
    #print current working dir
    # print(os.getcwd())

    # deploy_binaries(library_info, cmake_configuration, cmake_build_config)

    print(f"""                                  
    EXECUTING SIGNING AND CREATE ALIB FOR {library_info.name.upper()}

    creating the autolib by running createAlib function which will make
    a .alib file that we upload to azure/aws if you run the release command. Which will be done automatically on CI.                                         
    """)
    # if repository_library_release_info0.branch_type == "master" or repository_library_release_info0.branch_type == "develop" or repository_library_release_info0.branch_type == "main":
    print (f"       Creating autolib for {library_info.name}")
    
    remove_some_files_path = os.path.join(os.getcwd(), "out", "upload", cmake_configuration, cmake_build_config)
    
    extensions = [".pdb", ".debug", ".lib"]
    prefixes = ["[Data Page]", "Library.DeveloperState"]

    # if on ci remove the debug files else keep them
    if is_pipeline():
        for root, dirs, files in os.walk(remove_some_files_path):
            for file in files:
                if file.endswith(tuple(extensions)) or file.startswith(tuple(prefixes)):
                    print(f"Removing {file}")
                    os.remove(os.path.join(root, file))

    libraryRepo.createAlib(library_info.name, library_info.uuid, version, autolibToolset, cmake_configuration, cmake_build_config)
    
    print ("===============================================")
    return 1

def upload_to_symbol_store(repository_library_release_info, build_configs, cmake_configuration, base_path):  
    print(f"Uploading to symbol store from {base_path}")

    # walk the out folder and only get the paths where the last folder is called DLL
    directories = [os.path.join(root, name) for root, dirs, files in os.walk(base_path) for name in dirs if name == "DLL"]
    
    print (f"directories: {directories}")
    
    for directory in directories:
        # the toolset is in the directory two up from dll
        compiler, arch = cmake_configuration.split("@")
        print (f"compiler: {compiler} arch: {arch}")
        for library_info in repository_library_release_info.libraries:
            for build_config in build_configs:
                # if debug skip
                if build_config == "Debug":
                    continue
                autolibToolset = f"{compiler}_{arch}_{build_config}"
                parent_directory = os.path.dirname(directory)
                print(f"src: {directory} autolibToolset: {autolibToolset} version: {repository_library_release_info.project_version}")
                linux_debug_info_d.linux_debug_info_d( parent_directory, library_info.name, autolibToolset, repository_library_release_info.project_version)

def main():
    parser = argparse.ArgumentParser()
    # add arg --testing_debug_sym_upload
    parser.add_argument("--testing_debug_sym_upload", action="store_true")
    parser.add_argument("action")
    parser.add_argument("cmake_configuration", nargs='?')
    parser.add_argument("cmake_build_config", nargs='?')
    args = parser.parse_args()

    release_managers = os.getenv("RELEASE_MANAGER_NAMES", "").split(";")
    gitlab_user_name = os.getenv("GITLAB_USER_NAME", "")
    ci_job_manual = os.getenv("CI_JOB_MANUAL", None)
    print(f"RELEASE_MANAGER_NAMES: {release_managers}")
    print(f"GITLAB_USER_NAME: {gitlab_user_name}")
    print(f"CI_JOB_MANUAL: {ci_job_manual}")

    repository_library_release_info0 = repository_library_release_info(os.path.join(os.getcwd(), "repository_library_release.json"))
    print (repository_library_release_info0)

    # add a check for version arg
    if args.action == "version_check" or args.action == "release":

        aimmsRepo = 1
        schema = 'ToolsetLibraryRepository'
        connection = libraryRepo.getConnection(user='RepositoryUser', password='x538wKqjO1kl', host='mysql.intra.aimms.com', schema=schema)
        dict = libraryRepo.getAllFileInfoFromDb( connection, schema, aimmsRepo)
    
        # search if there already is a version that is the same as the current version matching first 3 numbers of the version
        # if so return 1 else return 0
        for key in dict['Libs']:
            # print (f"key: {key['id']} {key['version']}")
            # if id is the same as the current library
            if key['id'] == repository_library_release_info0.libraries[0].uuid:
                version_in_database = str(key['version']).split(".")
                version_in_database = version_in_database[0:3]
                
                current_version = repository_library_release_info0.project_version.split(".")
                current_version = current_version[0:3]
                
                #testing
                # current_version = "24.9.1.20".split(".")[0:3]
                
                if version_in_database == current_version:
                    print (f"Version {'.'.join(current_version)} already exists in the database found version {key['version']}")
                    exit(-1)

    cmake_build_configs = get_build_types()
    print (f"cmake_build_configs: {cmake_build_configs}")
    if args.action == "deploybinaries":
        
        for library_info in repository_library_release_info0.libraries:
            deploy_binaries(library_info, args.cmake_configuration, args.cmake_build_config)
        
    # new conan-cmake
    if args.action == "createlib":
        cmake_configurations = os.listdir(os.path.join(os.getcwd(), "out", "upload"))

        # filter out any non dir paths in cmake_configurations
        cmake_configurations = [config for config in cmake_configurations if os.path.isdir(os.path.join(os.getcwd(), "out", "upload", config))]

        print (f"cmake_configurations: {cmake_configurations}")
        # loop over the folder in out/upload these are the cmake configurations
        for cmake_configuration in cmake_configurations:
            for cmake_build_config in cmake_build_configs:
                
                base_path = os.path.join(os.getcwd(), "out", "upload", cmake_configuration, cmake_build_config)
                if (
                    repository_library_release_info0.branch_type == "master" or 
                    repository_library_release_info0.branch_type == "main" or 
                    repository_library_release_info0.branch_type == "feature/upload_symbols" or
                    args.testing_debug_sym_upload) and cmake_build_config == "RelWithDebInfo":
                    if is_pipeline():
                        print("on pipeline")
                        upload_to_symbol_store(repository_library_release_info0, cmake_build_configs, cmake_configuration, base_path)
                        signAutoLib(base_path, cmake_build_config)
                
                # check if exists
                if os.path.exists(os.path.join(os.getcwd(), "out", "upload", cmake_configuration, cmake_build_config)):
                    for library_info in repository_library_release_info0.libraries:
                        if library_info.is_sfx and repository_library_release_info0.is_windows:
                            print (f"Creating SFX for {library_info.name}")
                            createSfx(cmake_configuration, cmake_build_config, library_info, repository_library_release_info0.project_version)
                        elif not library_info.is_sfx:
                            ams_file = os.path.join(os.getcwd(), "out"  , "upload", cmake_configuration, cmake_build_config, library_info.name, library_info.ams_file)
                            libraryRepo.sed_inplace(ams_file, "__BUILDVERSION__", repository_library_release_info0.project_version)
                            createlib(cmake_configuration, cmake_build_config, library_info, repository_library_release_info0.project_version)
        
        return 0
    
    # This step will upload the autolib to our internal artifactory server for testing purposes
    if args.action == "upload":
        if is_pipeline():
            return libraryRepo.uploadAlibsToArtifactory(repository_library_release_info0)
        else: 
            print( "Cannot upload from local")
            return libraryRepo.uploadAlibsToArtifactory(repository_library_release_info0, dry_run=True)

	# This step will make an offcial release of the autolib on aws
    if args.action == "release":
        if is_pipeline():
            extra_protection = True if repository_library_release_info0.branch == "master" or repository_library_release_info0.branch == "main" else False
            
            if extra_protection:
                if ((gitlab_user_name in release_managers) and (ci_job_manual is not None)):
                    print(f"Hello {gitlab_user_name} I hope you are doing well! let's release the autolib!")
                    return libraryRepo.releaseAlibs(repository_library_release_info0, dry_run=False, hiddenRelease=False)
                else:
                    print(f"User {gitlab_user_name} not in the list of release managers")
                    exit(1)
            else:
                print(f"releasing to aws but with a specific branch type: {repository_library_release_info0.branch_type}")
                return libraryRepo.releaseAlibs(repository_library_release_info0, dry_run=False, hiddenRelease=False)
            
        else:
            print( "Cannot release from local")
            return libraryRepo.releaseAlibs(repository_library_release_info0, dry_run=True,hiddenRelease=True) # Hidden also True (no update db without upload)!
        
    if args.action == "revert":
        if is_pipeline():
            extra_protection = True if repository_library_release_info0.branch == "master" or repository_library_release_info0.branch == "main" else False

            if extra_protection:
                if ((gitlab_user_name in release_managers) and (ci_job_manual is not None)):
                    print(f"Hello {gitlab_user_name} I hope you are doing well! let's revert the autolib!")
                    return libraryRepo.revertRelease(repository_library_release_info0)
                else:
                    print(f"User {gitlab_user_name} not in the list of release managers")
                    exit(1)
        else:
            print("Cannot revert from local")

    return 0


if __name__ == "__main__":
    
    try:
        main()
    except Exception as e:
        print("Exception: %s" % e)
        # stacktrace
        import traceback
        traceback.print_exc()
        exit(1)
