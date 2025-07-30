import os
import shutil
import sys

sys.path.append(os.getcwd() + "/buildhelpers")
import argparse
import json
import internal.gitinfo as gitinfo
import cmake.aimms_artifactory as aimms_artifactory
import subprocess
import cmake.aimms_common as aimms_common

def search_conan_package_exists(package, version, branch):
    # execute conan search package/version@aimms/branch --format=json and check if the package exists
    ret = subprocess.run(['conan', 'search', f'{package}/{version}@aimms/{branch}', '--format=json', '-r', 'conan-intra'], capture_output=True)
    # decode the output
    output = ret.stdout.decode('utf-8')
    
    print (output)
    
    if '\"error\":' in output:
        return False
    
    return True

def print_quiet(string, quiet):
    if not quiet:
        print(string)

def print_banner(text):
    print('*' * len(text))
    print(text)
    print('*' * len(text))

def main(args):

    # read repository_library_release.json and get from the first library in libraries array the name
    # and set it as environment variable
    if os.path.exists('repository_library_release.json') == False:
        print_quiet(
            'repository_library_release.json not found so this is not an autolib project', args.quiet)
        sys.exit(1)

    with open('repository_library_release.json') as f:
        data = json.load(f)

    version = None
    branch = None
    
    if not args.branch is None:
        branch = args.branch
    if not args.version is None:
        version = args.version
        
    if version is None:
        version = "latest"
    
    if branch is None:
        branch = gitinfo.gitinfo().getFullBranchName().replace("/", "_").replace("-", "_")
    
    print(f"got from env version: {version} and branch: {branch}")
    
    if version == "latest" and args.pipeline_version_or_latest:
        version = gitinfo.gitinfo().getVersion()

    autolib_location = os.path.join(os.getcwd(), 'out', 'upload')
    autolib_conanfile_name = 'conanfile_autolib.py'
    autolib_conanfile_path = os.path.join(
        autolib_location, autolib_conanfile_name)

    os.makedirs(autolib_location, exist_ok=True)

    with open(autolib_conanfile_path, 'w') as f:
        # Write the necessary boilerplate for the conanfile.py
        f.write(
            '''
from conan import ConanFile

class AutoLibCollectorConan(ConanFile):
    license = "AIMMS"
    author = "developers@aimms.com"
    url = "https://gitlab.aimms.com/aimms/aimms"
    description = "generated"
    topics = ("deployment only")
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeDeps"
    package_type = "application"

    def requirements(self):
'''
        )

        for library in data['libraries']:
            i = 0
            
            # check if the library has conan_packages
            if 'conan_packages' not in library:
                print(f'Library {library["name"]} does not have conan_packages')
                continue
            
            conan_packages = library['conan_packages']

            if args.cmake:
                conan_packages = [
                    package for package in conan_packages if 'autolib' not in package]
                
                
            for package in conan_packages:
                requires = None
                if args.requires is not None:
                    if args.requires.__len__() > i:
                        requires = args.requires[i]
                    i += 1
                
                semver_version = aimms_artifactory.get_latest_version_artifactory(package, branch)
                if semver_version is None:
                    print(f'Could not find version for {package} in branch {branch} trying develop')
                    semver_version = aimms_artifactory.get_latest_version_artifactory(package, 'develop')
                    if semver_version is None:
                        print(f'Could not find version for {package} in branch develop')
                        exit(1)

                    f.write(f'        self.requires("{package}/{semver_version}@aimms/develop")\n')
                elif requires is not None:
                    requires_version = requires.split(':')[0]
                    requires_branch = requires.split(':')[1]
                    
                    # this is when you want to pick the latest version in the requires argument
                    if requires_version == 'latest':
                        requires_version = aimms_artifactory.get_latest_version_artifactory(package, requires_branch)
                    
                    # check if the package exists an if so add it to the requires
                    if search_conan_package_exists (package, requires_version, requires_branch):
                        f.write(f'        self.requires("{package}/{requires_version}@aimms/{requires_branch}")\n')
                    
                    # if the package does not exist in the conan repository then error
                    else:
                        print(f'Could not find version for {package} in branch {requires_branch}')
                        exit(1)
                
                elif args.pipeline_version_or_latest:
                    if search_conan_package_exists( package, version, branch):
                        print (f'Found pipeline version for {package} in branch {branch}')
                        f.write(f'        self.requires("{package}/{version}@aimms/{branch}")\n')
                        
                    else:
                        # get latest version from artifactory
                        print (f'Could not find version for {package} in branch {branch} trying latest')
                        fallback_latest_version = aimms_artifactory.get_latest_version_artifactory( package, branch)
                        if fallback_latest_version is None:
                            print_banner(f'Could not find version for {package} in branch {branch} trying develop')
                            fallback_latest_version = aimms_artifactory.get_latest_version_artifactory(
                                package, 'develop')
                            if fallback_latest_version is None:
                                print_banner(f'Could not find version for {package} in branch develop')
                                exit(1)

                            f.write(f'        self.requires("{package}/{fallback_latest_version}@aimms/develop")\n')
                        else:
                            f.write(f'        self.requires("{package}/{fallback_latest_version}@aimms/{branch}")\n')
                    
                # just pick latest if nothing else is specified     
                else:
                    f.write(f'        self.requires("{package}/{semver_version}@aimms/{branch}")\n')

    print_quiet(f'{autolib_conanfile_name} generated', args.quiet)

    cmake_configs = aimms_common.get_configurations()
    cmake_build_types = aimms_common.get_build_types()

    profiles = []

    for config in cmake_configs:
        profile = aimms_common.get_config_conan_profile(config).replace("${sourceDir}/", "")
        if profile not in profiles:
            profiles.append(profile)

    print_quiet(f'Profiles: {profiles}', args.quiet)

    os.environ['LIBRARYNAME'] = data['libraries'][0]['name']
    print_quiet(f'LIBRARYNAME: {data["libraries"][0]["name"]}', args.quiet)

    if args.dry:
        print_quiet('Dry run', args.quiet)
        sys.exit(0)

    if args.cmake_preset != 'all':
        # split args.cmake_preset
        args_compiler = args.cmake_preset.split('@')[0]

        # filter out the profiles that match the cmake_preset if profile ends arg.cmake_preset than keep it
        profiles = [profile for profile in profiles if profile.endswith(args_compiler)]

    print_quiet(f'Going to run with profiles: {profiles}', args.quiet)

    # filter out of the profiles gcc13
    profiles = [profile for profile in profiles if 'gcc13' not in profile]

    for profile in profiles:
        for build_type in cmake_build_types:
            if args.cmake_build_type != 'all' and args.cmake_build_type != build_type:
                continue
            print_quiet(f'Profile: {profile} Build type: {build_type}', args.quiet)
            compiler = profile.split("/")[-1]
            arch = profile.split("/")[-2]
            combined = f"{compiler}@{arch}"
            ret = subprocess.run(['conan', 'install', autolib_conanfile_path, '--profile:host', f'{profile}/{build_type}', '--profile:build', f'{profile}/build',
                                 f'--deployer={os.getcwd()}/buildhelpers/autolibs/alib_deploy.py', '--deployer-folder', f'{os.getcwd()}/out/upload/{combined}/{build_type}', '-of', 'out/conan_output'], capture_output=args.quiet)

            # make a file called _mininalAIMMSversion_.txt that has the minimal AIMMS version that is required from the data['libraries'][0]['minveraimms']
            name  = data['libraries'][0]['name']
            with open(f'{os.getcwd()}/out/upload/{combined}/{build_type}/{name}/_mininalAIMMSversion_.txt', 'w') as f:
                try:
                    f.write(data['libraries'][0]['minveraimms']) 
                except Exception as e:
                    print(f'Could not find minveraimms in repository_library_release.json: {e}')
                    f.write('24.0')
            
            # remove conaninfo.txt and conanbuildinfo.txt from antwhere in  f'{os.getcwd()}/out/upload/{combined}/{build_type}'
            for root, dirs, files in os.walk(f'{os.getcwd()}/out/upload/{combined}/{build_type}'):
                for file in files:
                    if file == 'conaninfo.txt' or file == 'conanbuildinfo.txt' or file == 'conanmanifest.txt':
                        os.remove(os.path.join(root, file))

                # if dir name is remove than remove the dir
                for dir in dirs:
                    if dir == 'remove':
                        # get parent dir of root
                        parent = os.path.join(root, os.pardir)
                        
                        # if the folder already exists then remove it
                        if os.path.exists(os.path.join(parent, 'non_autolib_artifacts')):
                            shutil.rmtree(os.path.join(parent, 'non_autolib_artifacts'))
                        
                        shutil.move(os.path.join(root, dir), os.path.join(parent, 'non_autolib_artifacts'))
                
        

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--cmake_preset', type=str,
                        help='CMake preset', default='all', required=False)
    parser.add_argument('--cmake_build_type', type=str,
                        help='CMake build type', default='all', required=False)
    parser.add_argument('--dry', action='store_true', help='Do a dry run')
    parser.add_argument('--quiet', action='store_true', help='Suppress output')
    parser.add_argument('--cmake', action='store_true', help='Verbose output')
    parser.add_argument('--pipeline_version_or_latest', action='store_true', help='Overwrite requirements with latest')
    parser.add_argument('--branch', type=str, help='Branch name', required=False) 
    parser.add_argument('--version', type=str, help='Version name', required=False)
    # an array of requires strings
    parser.add_argument('--requires', nargs='+', help='Requires', required=False)

    args = parser.parse_args()

    main(args)
