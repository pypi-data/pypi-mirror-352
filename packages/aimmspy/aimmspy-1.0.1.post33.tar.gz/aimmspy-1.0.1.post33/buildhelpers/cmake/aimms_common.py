# Description: Common functions for aimms build scripts these functions are used by the aimms build scripts in
# cmakelists conan_install2 and for example as well as run in the pipeline like buildCmake.py and conan_build_and_upload.py

import io
import shutil
import sys
import subprocess
import os
import json
import platform
import datetime


def is_windows():
    return platform.system().lower() == 'windows'


def is_linux():
    return platform.system().lower() == 'linux'


def executeCmd(_cmdLine, _cwd=None, exitOnFail=True, start_new_session=False, silent=False):
    process = subprocess.Popen(_cmdLine, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               text=True, shell=True, cwd=_cwd, start_new_session=start_new_session)

    while True:
        output_line = process.stdout.readline()
        if output_line == '' and process.poll() is not None:
            break

        if output_line:
            # timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            # if not silent:
            #     print(f'[{timestamp}] {output_line.strip()}')
                
            if not silent:
                print(f'{output_line.strip()}')

    if exitOnFail and process.returncode != 0:
        sys.exit(1)
    return process.returncode


def dos2unix(filename):
    with io.open(filename, 'r') as f:
        text = f.read()
    with io.open(filename, 'w', newline='\n') as f:
        f.write(text)


def get_profile_multi():
    preset = os.environ.get('preset')
    if preset:
        compiler = preset
    else:
        raise RuntimeError('preset environment variable not set')

    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'aimms_presets.json'), 'r') as f:
        presets = json.load(f)

    for preset in presets['configurePresets']:
        if preset['name'] == f'{compiler}':
            return compiler

    raise ValueError(f'invalid preset: {compiler}')


def is_windows(compiler):
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'aimms_presets.json'), 'r') as f:
        presets = json.load(f)

    for preset in presets['configurePresets']:
        if compiler in preset['name']:
            return 'windows' in preset['inherits']

def is_linux(compiler):
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'aimms_presets.json'), 'r') as f:
        presets = json.load(f)

    for preset in presets['configurePresets']:
        if compiler in preset['name']:
            return 'linux' in preset['inherits']

def get_build_types():
    build_types = []
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'aimms_presets.json'), 'r') as f:
        presets = json.load(f)
        # get from ConfigurePresets the first and from cacheVariables get CMAKE_CONFIGURATION_TYPES
        for preset in presets['configurePresets']:
            if "default-configuration" in preset['name']:
                build_types = preset['cacheVariables']['CMAKE_CONFIGURATION_TYPES'].split(
                    ';')
                break
    return build_types


def get_configurations():
    configurations = []
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'aimms_presets.json'), 'r') as f:
        presets = json.load(f)
        # get from ConfigurePresets the first and from cacheVariables get CMAKE_CONFIGURATION_TYPES
        for preset in presets['configurePresets']:
            if not "default" in preset['name']:
                configurations.append(preset['name'])
    return configurations


def get_config_conan_profile(config):
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'aimms_presets.json'), 'r') as f:
        presets = json.load(f)
        # get from ConfigurePresets the first and from cacheVariables get CMAKE_CONFIGURATION_TYPES
        for preset in presets['configurePresets']:
            if preset['name'] == config:
                for cacheVariable in preset['cacheVariables']:
                    if cacheVariable == 'CONAN_PROFILE':
                        return preset['cacheVariables'][cacheVariable]
    return None


def get_correct_toolset(compiler, arch):
    cmake_label_toolset = compiler
    if is_windows(compiler):
        # open the aimms_presets.json file
        with open(os.path.join(os.getcwd(), "buildhelpers", "cmake", "aimms_presets.json")) as json_file:
            data = json.load(json_file)
            for preset in data["configurePresets"]:
                if preset["name"] == f"{compiler}@{arch}":
                    toolset_value = preset["toolset"]["value"]
                    # split toolset value at the , and get first part
                    cmake_label_toolset = toolset_value.split(",")[0]
                    # change v to vc
                    cmake_label_toolset = cmake_label_toolset.replace(
                        "v", "vc")
                    break
    return cmake_label_toolset


def get_autolib_arch(arch, compiler):
    # if on linux and arch is x86_64, change to linux64 if on windows and arch is x86_64, change to x64
    if is_linux(f'{compiler}@{arch}'):
        if arch == 'x86_64':
            return 'linux64'
    elif is_windows(f'{compiler}@{arch}'):
        if arch == 'x86_64':
            return 'x64'

def get_autolib_cmake_build_type(build_type):
    # if RelWithDebInfo, change to Release
    if build_type == 'RelWithDebInfo':
        return 'Release'
    return build_type

def get_alib_name(compiler, arch, build_type):
    return f'{get_autolib_arch(arch, compiler)}_{get_correct_toolset(compiler, arch)}_{get_autolib_cmake_build_type(build_type)}.alib'

def sign_binaries(compiler):
    from conan_signtool import signBinaries
    
    branch = None
    
    try:
        from gitinfo import gitinfo
    
        git = gitinfo()
        branch = git.getFullBranchName()
        print (f'Branch: {branch}')
    except ImportError:
        branch = None
    
    if is_windows(compiler) and (branch == 'master' or branch == 'main' or branch == 'develop' or branch == None):
        build_types = get_build_types()
        for build_type in build_types:
            if build_type == 'Release' or build_type == 'RelWithDebInfo':
                path = os.path.abspath(os.path.join(
                    'out', 'install', f'{compiler}', build_type))
                dotnet_path = os.path.abspath(
                    os.path.join('tmp', 'csc20_Release'))
                # if folder exists, sign binaries
                if os.path.exists(path):
                    signBinaries(path)
                if os.path.exists(dotnet_path):
                    signBinaries(dotnet_path)


def get_conanfile_name():
    executeCmd("conan inspect . --format=json")
    conan_inspect = subprocess.run(
        ['conan', 'inspect', '.', '--format=json'], stdout=subprocess.PIPE).stdout.decode('utf-8').rstrip()
    # parse conan inspect to get the name
    conan_inspect_json = json.loads(conan_inspect)
    return conan_inspect_json['name']


def copytree(src, dst, symlinks=False, ignore=None):
    if not os.path.exists(dst):
        os.makedirs(dst)
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            copytree(s, d, symlinks, ignore)
        else:
            if not os.path.exists(d) or os.stat(s).st_mtime - os.stat(d).st_mtime > 1:
                shutil.copy2(s, d)


def repo_dirty(throw=True):
    ret = subprocess.run(['git', 'status', '-s'], stdout=subprocess.PIPE)
    output = ret.stdout.decode('utf-8').strip()

    if output != '' and throw:
        raise RuntimeError(
            f'There are changes in the git repo:\n{output}\nPlease commit them before exporting the package.')
