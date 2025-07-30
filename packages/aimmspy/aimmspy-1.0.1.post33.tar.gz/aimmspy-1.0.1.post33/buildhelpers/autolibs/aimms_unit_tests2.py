import platform
import subprocess
import sys
import os


sys.path.append(os.path.join(os.getcwd()))
sys.path.append(os.path.join(os.getcwd(), "buildhelpers"))
sys.path.append(os.path.join(os.getcwd(), "buildhelpers", "conan"))
sys.path.append(os.path.join(os.getcwd(), "buildhelpers", "cmake"))

import json
from autolib_unit_test import runProjectTests
import argparse
from autolibs.autolib_common import extract_alib
from aimms_artifactory import get_latest_version_artifactory
from deploy_aimms import deploy_aimms
import buildhelpers.gitinfo as gitinfo

def main( args ):
    
    # check if there is a aimmsversion.env file
    if os.path.exists(os.path.join(os.getcwd(), 'aimmsinfo.env')):
        print ("Found aimmsinfo.env file")
        # set the environment variables
        with open(os.path.join(os.getcwd(), 'aimmsinfo.env'), 'r') as f:
            for line in f:
                print (line)
                key, value = line.strip().split('=')
                os.environ[key] = value
        
    version = None
    branch = None
    
    if not args.branch is None:
        branch = args.branch
    if not args.version is None:
        version = args.version
        
    if os.getenv("AIMMS_TEST_VERSION") is not None:
        version = os.getenv("AIMMS_TEST_VERSION")
        
    if os.getenv("AIMMS_TEST_BRANCH") is not None:
        branch = os.getenv("AIMMS_TEST_BRANCH")
        
    if version is None:
        version = "latest"
    
    if branch is None:
        branch = "master"
    
    print(f"got from env version: {version} and branch: {branch}")
    
    if version == "latest":
        version = str(get_latest_version_artifactory("aimms", branch))

    print (f"Testing version {version} on branch {branch}")

    with open(os.path.join(os.getcwd(), 'repository_library_release.json')) as f:
        repository_library_release = json.load(f)
        
    template_path = os.path.join(os.getcwd(), repository_library_release['libraries'][0]['template_path'])
    template_path = os.path.normpath(template_path)

    extra_args = repository_library_release['libraries'][0].get('extra_args', [])
    # get the skip test list if exists in the repository_library_release.json
    skip_tests = repository_library_release['libraries'][0].get('skip_tests', [])
    
    # if pip_requirements is set in the repository_library_release.json then install the requirements needed for PythonProvider for example
    # this is needed for the tests to run with aimms_api_py
    pip_requirements_path = repository_library_release['libraries'][0].get('pip_requirements_path', None)
    if pip_requirements_path is not None:
        artifactory_username = os.getenv("ARTIFACTORY_USERNAME")
        artifactory_password = os.getenv("ARTIFACTORY_PASSWORD")
        
        if platform.system() == "Linux":
            import sysconfig
            #append to the LD_LIBRARY_PATH the path to the current python lib folder
            os.environ["LD_LIBRARY_PATH"] += ":" + sysconfig.get_config_var('LDLIBRARY')
        
        # set environment variable AIMMSPYTHONVERSION based on the python thats currently running should be like 310 311 etc
        python_version = sys.version_info
        os.environ["AIMMSPYTHONVERSION"] = f"{python_version.major}{python_version.minor}"
        
        if artifactory_username is None or artifactory_password is None:
            print ("ARTIFACTORY_USERNAME and ARTIFACTORY_PASSWORD must be set in the environment")
            exit(1)
        
        os.environ["PIP_EXTRA_INDEX_URL"] = f"https://{artifactory_username}:{artifactory_password}@artifactory.platform.aimms.com/artifactory/api/pypi/pypi/simple"
        
        pip_requirements_path = os.path.join(os.getcwd(), pip_requirements_path).replace("\\", "/")
        print (f"Installing pip requirements from {pip_requirements_path}")
        ret = subprocess.run(["pip", "install", "-r", pip_requirements_path], capture_output=True, text=True, env=os.environ)
        print (ret.stdout)
        if ret.returncode != 0:
            print (f"Failed to install pip requirements from {pip_requirements_path}")
            print (ret.stderr)
            exit(1)
        print (f"Successfully installed pip requirements from {pip_requirements_path}")
    

    # the skip tests is a list with objects containing cmake_preset and cmake_build_type if this matches the current test then skip
    for skip_test in skip_tests:
        if skip_test['cmake_preset'] == args.cmake_preset and skip_test['cmake_build_type'] == args.cmake_build_type:
            print (f"Skipping this test {skip_test}")
            exit(0)
            
    
    arch = args.cmake_preset.split('@')[1]
    version = deploy_aimms(args.cmake_preset, branch, args.cmake_build_type, version, True)
    # ---------------------------------------------------------------------------------------------------
    # unpack a alib found in out/upload folder
    # ---------------------------------------------------------------------------------------------------
    # UNPACK ALIB
    # ---------------------------------------------------------------------------------------------------
    
    semver_version = gitinfo.gitinfo().getVersion()
    auto_lib_version = semver_version.replace("-", ".")
    
    if args.dry:
        exit(0)
    
    if not args.cmake:
        extract_alib(args.cmake_preset, args.cmake_build_type, auto_lib_version)
    
    # ---------------------------------------------------------------------------------------------------
    # AIMMS UNIT TESTS
    # ---------------------------------------------------------------------------------------------------
    main_project_path = os.path.join(os.path.dirname(template_path), 'MainProject')
    autolib_path = os.path.join(os.getcwd(), 'out', 'upload', args.cmake_preset,
                          args.cmake_build_type, repository_library_release['libraries'][0]['name'])

    # open the xml aimms file template and append MainProject and Library paths
    with open(template_path, 'r') as file:
        data = file.readlines()

    # insert into References AIMMS_Version the MainProject and Library paths
    data.insert(2, f"   <MainProject Path=\"{main_project_path}\"/>\n")
    data.insert(3, f"   <Library Path=\"{autolib_path}\"/>\n")

    # write the new xml aimms file to the same path as the template but with the preset and config name
    from_template_file = os.path.join(os.path.dirname(template_path),
                        f"{args.cmake_preset}_{args.cmake_build_type}.aimms")
    with open(from_template_file, 'w') as file:
        file.writelines(data)

    with open(from_template_file, 'r') as file:
        data = file.read()    

    print (f"Running tests with {from_template_file}")
    print (f".aimms is \n{data}")

    # run the aimms tests
    result = runProjectTests(version, arch, args.cmake_build_type, os.path.dirname(template_path), os.path.basename(from_template_file), os.getcwd(), '', extra_args=extra_args, custom_procedure=args.procedure)
    
    if result != 0:
        exit(result)
    
if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--cmake_preset', type=str, required=True, help='CMake preset')
    parser.add_argument('--cmake_build_type', type=str, required=True, help='CMake build type')
    parser.add_argument('--dry', action='store_true', help='Do a dry run')
    parser.add_argument('--cmake', action='store_true', help='Run from cmake')
    parser.add_argument('--version', type=str, help='Version to test', default=None)
    parser.add_argument('--branch', type=str, help='Branch to test', default=None)
    parser.add_argument('--procedure', type=str, help='Procedure to run', default=None)
    args = parser.parse_args()
    
    print (f"Running tests with {args}")
    
    main(args)
