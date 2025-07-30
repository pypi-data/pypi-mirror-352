from asyncio import sleep
import fnmatch
import platform
import sys
import os
import argparse
import subprocess

sys.path.append(os.path.join(os.getcwd()))
sys.path.append(os.path.join(os.getcwd(), "buildhelpers"))
sys.path.append(os.path.join(os.getcwd(), "buildhelpers", "conan"))
sys.path.append(os.path.join(os.getcwd(), "buildhelpers", "cmake"))

from aimms_artifactory import get_latest_version_artifactory
from deploy_aimms import deploy_aimms

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--version', type=str, help='Version to test', default=None)
parser.add_argument('--branch', type=str, help='Branch to test', default=None)
parser.add_argument('--cmake_preset', type=str, help='CMake preset', default=os.getenv("preset", "msvc193@x86_64"))
parser.add_argument('--cmake_build_type', type=str, help='CMake build type', default=os.getenv("build_type", "Debug"))
parser.add_argument('--dry', action='store_true', help='Dry run')
parser.add_argument('--local', action='store_true', help='Install locally')
args = parser.parse_args()

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

arch = args.cmake_preset.split('@')[1]
os.environ['AIMMS_FOLDER_DEPLOY_VERSION_NAME'] = "latest"
version = deploy_aimms(args.cmake_preset, branch, args.cmake_build_type, version, True)

aimms_folder = os.path.join(os.getcwd(), 'aimms', "latest", args.cmake_build_type, 'Bin')

if not os.environ.get('AIMMSPATH'):
    os.environ['AIMMSPATH'] = aimms_folder
print (f"set AIMMSPATH to {os.environ['AIMMSPATH']}")

compiler, arch = args.cmake_preset.split('@')


if args.dry:
    print("Dry run")
    sys.exit(0)


if not args.local:
    dist_folder = "./dist"
    print(f"Installing aimmspy from {dist_folder}")

    # print the files in dist_folder
    for file in os.listdir(dist_folder):
        print(f"Found file: {file}")
 
    print(f"pip install --find-links {dist_folder} aimmspy")
    os.system(f"pip install --find-links {dist_folder} aimmspy")
                    
failure = False

print(f"Python version: {sys.version}")

for file in os.listdir(os.path.join(os.getcwd(), "aimms_api_py", "python")):
    if (file.startswith("test_") or ( args.cmake_build_type == "RelWithDebInfo" and file.startswith("dataframe_test_"))) and file.endswith(".py"):
        print(f"running test or benchmark: {file}")
        
        try:
            # set the environment variable LOG_DIR 
            # get the file name without the extension
            file_name = os.path.splitext(file)[0]
            os.environ['LOG_DIR'] = os.path.join(os.getcwd(), "aimms_api_py", "python", "logs", file_name)
            
            
            ret = subprocess.run([sys.executable, os.path.join(os.getcwd(), "aimms_api_py", "python", file)], timeout=300, capture_output=True)
            print (ret.stdout.decode())
            print (ret.stderr.decode())
            print (f"return code: {ret.returncode}")
            print("-------------------------------------------------------\n\n")
            # flush the output
            sys.stdout.flush()
            sys.stderr.flush()
    
            if 'handles were not deleted' in ret.stderr.decode():
                print(f"Test {file} failed with error: {ret.stderr.decode()}")
                sys.exit(1)
            
            if ret.returncode != 0:
                print(f"Test {file} failed with return code {ret.returncode}")
                failure = True
        except subprocess.TimeoutExpired:
            print(f"Test {file} timed out")
            failure = True
        except Exception as e:
            print(f"Test {file} failed with exception: {e}")
            failure = True

if failure:
    print ("One or more tests failed")
    sys.exit(1)
