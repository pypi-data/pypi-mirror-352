import argparse
import platform
import sys
import os
import logging

from aimms_artifactory import quit_job_if_on_artifactory
from aimms_common import executeCmd, get_conanfile_name, get_profile_multi, get_build_types, sign_binaries
import conan_login

sys.path.append(os.path.join(os.getcwd()))
from buildhelpers.gitinfo import gitinfo  # noqa: E402

def safe_getenv(key):
    if key in os.environ:
        return os.environ[key]
    else:
        raise Exception(f'{key} is not set')

def conan_style_mode(args):
    compiler = args.local_build
    
    compiler_complete = None
    if not args.local_build:
        compiler_complete = get_profile_multi()

        # split compiler into arch and compiler
        split = compiler_complete.split('@')
        compiler = split[0]
        arch = split[1]
    else:
        split = compiler.split('@')
        compiler = split[0]
        arch = split[1]

    # current path
    working_folder = os.getcwd()
    
    # check if env conan_profiles_path is set
    print (os.environ)
    profile_dir = safe_getenv('conan_profiles_path')
    
    profile_dir = os.path.join(
        working_folder, profile_dir)

    # get build type from env
    build_type = safe_getenv('build_type')

    gi = gitinfo()
    branch = gi.getFullBranchName()
    version = gi.getVersion()

    executeCmd("conan remote list", working_folder)
    if not args.local_build:
        conan_login.login()

    executeCmd('git diff')
    
    print (f'compiler: {compiler}')
    print (f'arch: {arch}')

    # for build_type in build_types:
    executeCmd(
            f"conan create . -pr:h {profile_dir}/{build_type} -pr:b {profile_dir}/build --channel={branch} --user=aimms --version={version}", working_folder)

    name = get_conanfile_name()
    full_qualified_package_name = f'{name}/{version}@aimms/{branch}'

    executeCmd('git diff')
    
    sign_binaries(compiler_complete)
    
    if not args.local_build:
        quit_job_if_on_artifactory(name, version, branch, compiler_complete, build_type=build_type)
        
        if not args.dry:
            executeCmd(f"conan upload -vtrace {full_qualified_package_name} -r conan-intra", working_folder)


def dotnet(args):
    compiler = args.local_build
    
    compiler_complete = None
    if not args.local_build:
        compiler_complete = get_profile_multi()

        # split compiler into arch and compiler
        split = compiler_complete.split('@')
        compiler = split[0]
        arch = split[1]
    else:
        split = compiler.split('@')
        compiler = split[0]
        arch = split[1]

    # current path
    working_folder = os.getcwd()
    profile_dir = os.path.join(
        working_folder, "buildhelpers", "conan-profiles", platform.system().lower())

    # for configuration type
    build_types = get_build_types()

    gi = gitinfo()
    branch = gi.getFullBranchName()
    version = gi.getVersion()

    # vs_path = terminal_command(compiler, local_build, True)

    name = get_conanfile_name()
    full_qualified_package_name = f'{name}/{version}@aimms/{branch}'

    print(f'package recipe: {full_qualified_package_name}')

    executeCmd("conan remote list", working_folder)
    if not args.local_build:
        conan_login.login()
    
    print (f'compiler: {compiler}')
    print (f'arch: {arch}')

    if not args.local_build:
        quit_job_if_on_artifactory(name, version, branch, compiler_complete)

    for build_type in build_types:
        fake_build_type = build_type
        if build_type == "RelWithDebInfo":
            fake_build_type = "Release"
        executeCmd(f'buildit.bat {fake_build_type} {compiler}', working_folder)
        # executeCmd('git diff')
    
        if not args.local_build:
            sign_binaries(compiler_complete)
        
            executeCmd(f"conan export-pkg {working_folder} --profile:build={profile_dir}/{arch}/{compiler}/{build_type} --profile:host={profile_dir}/{arch}/{compiler}/{build_type} --name {name} --version {version} --user aimms --channel {branch} --output-folder=tmp/csc20_{fake_build_type}")
        
            if not args.dry:
                executeCmd(f"conan upload -vtrace {full_qualified_package_name} -r conan-intra")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--local_build', help='local build')
    parser.add_argument('--dotnet', action='store_true', help='dotnet build')
    parser.add_argument('--dry', action='store_true', help='dry run')
    args = parser.parse_args()

    try:
        if args.dotnet:
            dotnet(args)
        else:
            conan_style_mode(args)

    except Exception as e:
        logging.fatal(e.with_traceback())
        sys.exit(1)
