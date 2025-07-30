import sys
import os


sys.path.append(os.path.join(os.getcwd()))
sys.path.append(os.path.join(os.getcwd(), "buildhelpers"))
sys.path.append(os.path.join(os.getcwd(), "buildhelpers", "conan"))
sys.path.append(os.path.join(os.getcwd(), "buildhelpers", "cmake"))

import py7zr
import shutil
import json
from aimms_common import get_alib_name

def extract_alib(cmake_preset, cmake_build_type, auto_lib_version):

    compiler = cmake_preset.split('@')[0]
    arch = cmake_preset.split('@')[1]

    with open(os.path.join(os.getcwd(), 'repository_library_release.json')) as f:
        repository_library_release = json.load(f)

    alib_path = os.path.join(os.getcwd(), 'out', 'upload', cmake_preset, 'libs',
    repository_library_release['libraries'][0]['uuid'], auto_lib_version, get_alib_name(compiler, arch, cmake_build_type))

    if os.path.exists(alib_path):
        alib_path_unpack = os.path.join(os.getcwd(), 'out', 'upload', cmake_preset,
                                        cmake_build_type, repository_library_release['libraries'][0]['name'])
        # unzip the alib

        # remove the existing folder
        # If you get a permission error, this means that the folder is still in use by another process
        if os.path.exists(alib_path_unpack):
            shutil.rmtree(alib_path_unpack)

        print(f"Unpacking alib {alib_path}")
        with py7zr.SevenZipFile(alib_path, mode='r') as zip_ref:
            zip_ref.extractall(alib_path_unpack)
        # move the alib to the correct location by moving it one directory up
        extracted_path = os.path.join(alib_path_unpack, os.path.splitext(
            get_alib_name(compiler, arch, cmake_build_type))[0])
        # move to existing folder to a dummy folder and than move the dummy folder to the correct location
        shutil.move(extracted_path, os.path.join(os.getcwd(), 'out',
                    'upload', cmake_preset, cmake_build_type, "dummy"))
        # remove the empty directory
        os.rmdir(alib_path_unpack)
        shutil.move(os.path.join(os.getcwd(), 'out', 'upload',
                    cmake_preset, cmake_build_type, "dummy"), alib_path_unpack)






