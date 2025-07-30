import sys
import subprocess
import os
import argparse
import json
import logging
import yaml
import tempfile
        
from aimms_common import *
import conan_login


class warning_banners:
    build_helpers_branch_and_yaml = '''
===========================================================================================================================
Possible error:
    - The repo's submodule Buildhelpers branch doesn't match the included submodule Buildhelpers branch in .gitlab-ci.yml
    - Submodule Buildhelpers is behind on the head of it's branch
===========================================================================================================================
'''


def repo_check():

    result = subprocess.run(
        ['git', 'submodule', 'status', 'buildhelpers'], stdout=subprocess.PIPE)

    command_output = result.stdout.decode('utf-8').strip()
    submodule_branch = command_output.split(' ')[2]

    submodule_branch_name = submodule_branch[1:-1]
    if submodule_branch_name.startswith('remotes/origin/'):
        submodule_branch_name = submodule_branch_name[15:]
    elif submodule_branch_name.startswith('heads/'):
        submodule_branch_name = submodule_branch_name[6:]

    print(f'Buildhelpers submodule branch: {submodule_branch_name}')

    if os.path.exists('.gitlab-ci.yml'):
        with open('.gitlab-ci.yml', 'r') as f:
            root_ci = yaml.safe_load(f)

        include_ci = root_ci['include']
        for included in include_ci:
            if included['project'] == 'aimms/submodules/buildhelpers':
                print(
                    f'Buildhelpers submodule included in .gitlab-ci.yml: {included["ref"]}')
                if (included['ref'] == 'master' or included['ref'] == 'main') and submodule_branch_name == 'HEAD':
                    return 0
                elif included['ref'] != submodule_branch_name:
                    # raise RuntimeError(f'buildhelpers submodule is incorrectly included in .gitlab-ci.yml, should be: {submodule_branch_name}')
                    return 1
                else:
                    return 0
            else:
                raise RuntimeError(
                    'Buildhelpers submodule is not included in .gitlab-ci.yml, should be: -project: aimms/submodules/buildhelpers')
    else:
        raise RuntimeError('No .gitlab-ci.yml file found')


def cmake_build_multi(compiler, aimms_presets_path, local_build=False):

    configuration_types = []
    
    # if ci variable build_type is set than use that as the build type
    if os.environ.get('build_type'):
        configuration_types.append(os.environ.get('build_type'))
    else:
        configuration_types = get_build_types()

    build_command = f'cmake --preset={compiler}'

    # loop over all configuration types
    for configuration_type in configuration_types:

        build_command += f' && cmake --build --preset={compiler}_{configuration_type}_build --config {configuration_type}'

    for configuration_type in configuration_types:
        build_command += f' && ctest --preset={compiler}_{configuration_type}_test --config {configuration_type}'
        
    for configuration_type in configuration_types:
        build_command += f' && cmake --install out/build/{compiler} --config {configuration_type}'

    executeCmd(build_command)
    
    # check if in the cwd there is a repository_library_release.json file
    cwd = os.getcwd()
    if os.path.exists(os.path.join(cwd, 'repository_library_release.json')):
        print ("repository_library_release.json found")
        path = os.path.abspath(os.path.join(cwd, 'repository_library_release.json'))
        # open the repository_library_release.json file
        
        sys.path.append(os.getcwd() + "/buildhelpers")
        import internal.gitinfo as gitinfo
        import json
        gitinfo0 =  gitinfo.gitinfo()
        version = gitinfo0.getVersion()
        branch = gitinfo0.getFullBranchName()
        
        if (branch == 'main' or branch == 'master' or branch == 'feature/upload_symbols') and configuration_type == 'RelWithDebInfo' and platform.system() == 'Windows':
            with open(path) as rlrj:
                data = json.load(rlrj)
                library = data['libraries'][0]
                name = library['name']
                compiler_part, arch = compiler.split('@')
                autolibToolset = f"{compiler_part}_{arch}_{configuration_type}"
            
                print ("Trying to upload symbols")
                sys.path.append(os.path.join(os.getcwd(), "buildhelpers", "cmake"))
                sys.path.append(os.path.join(os.getcwd()))
                import buildtool.generalBuildSupport as gbs
                bin_path = os.path.abspath(os.path.join(cwd, 'out', 'install', compiler, configuration_type,"DLL"))
                try:
                    gbs.exportSymbolStore(bin_path, name,  autolibToolset, version )
                    print ("Symbols uploaded")
                except Exception as e:
                    print (f"Error while uploading symbols: {e}")
    
def conan_upload(aimms_presets_path):
    with open(aimms_presets_path, 'r') as f:
        presets = json.load(f)
    
    for preset in presets['configurePresets']:
        if preset['name'] == f'default-configuration':
            minimum_cmake = preset['cacheVariables']["MINIMUM_CMAKE_VERSION"]
    
    print("git diff")
    subprocess.check_output(["git", "diff"])
    executeCmd(
        f'cmake -B {tempfile.gettempdir()} -DCONAN_UPLOAD="ON" -DMINIMUM_CMAKE_VERSION={minimum_cmake}')


def multi_config_mode(aimms_presets_path, local_build=False):
    # ---------------------------------------------------------------------------- #
    #          the get_profile_multi will get the profile that is set by the
    #          .gitlab-ci.yml file. This is needed because it is tied to
    #          a specific job and docker build image.
    # ---------------------------------------------------------------------------- #
    compiler = get_profile_multi()
    # ---------------------------------------------------------------------------- #
    #           the check phase will execute some code before anything else
    #           for example check if the buildhelpers submodule is correctly
    #           included in the .gitlab-ci.yml file and the branch name are
    #           the same. Or check if the line endings are correct. Because
    #           in conan 2 that can cause problems with revisions.
    # ---------------------------------------------------------------------------- #
    if args.check:
        if repo_check() == 1:
            logging.warning(warning_banners.build_helpers_branch_and_yaml)
    # ---------------------------------------------------------------------------- #
    #           The build will start based on the profile that is set by the
    #           .gitlab-ci.yml file. Also the binaries will be signed if the
    #           profile is windows and release. because those will be shipped
    #           to the customers.
    # ---------------------------------------------------------------------------- #
    elif args.build:
        cmake_build_multi(compiler, aimms_presets_path, local_build)
        sign_binaries(compiler)
    else:
        parser.print_help()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--login", action='store_true',
                       help='login to conan server')
    group.add_argument('--check', action='store_true',
                       help='check prerequisite')
    group.add_argument('--package', action='store_true',
                       help='package and upload')
    group.add_argument('--build', action='store_true', help='build')

    parser.add_argument('--multi', action='store_true', help='multi config')

    parser.add_argument(
        '--local_build', action='store_true', help='local build')

    args = parser.parse_args()

    aimms_presets_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'aimms_presets.json')

    try:
        if args.package:
            conan_upload(aimms_presets_path)
        elif args.multi:
            multi_config_mode(aimms_presets_path, args.local_build)
        elif args.login:
            conan_login.login()

    except Exception as e:
        logging.fatal(e)
        sys.exit(1)
