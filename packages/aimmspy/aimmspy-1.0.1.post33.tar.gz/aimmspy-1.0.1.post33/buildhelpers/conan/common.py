import os
import json
from conan import ConanFile 
from conan.tools.files import copy, rm

def handle_presets(build_folder, settings):
    compiler = settings.compiler
    compiler_version = settings.compiler.version
    arch = settings.arch
    build_type = settings.build_type

    presets_path = os.path.join(build_folder, "buildhelpers", "cmake", "aimms_presets.json")
    with open(presets_path, "r") as f:
        presets = json.load(f)
        for preset in presets["configurePresets"]:
            if preset["name"] == f"{compiler}{compiler_version}@{arch}":
                break
        else:
            presets["configurePresets"].append({
                "name": f"{compiler}{compiler_version}@{arch}",
                "generator": "Ninja Multi-Config",
                "cacheVariables": {
                    "CONAN_PROFILE": f"${{sourceDir}}/buildhelpers/conan-profiles/{str(settings.os).lower()}/{arch}/{compiler}{compiler_version}",
                    "CMAKE_C_COMPILER": "cl.exe",
                    "CMAKE_CXX_COMPILER": "cl.exe"
                },
                "toolset": {
                    "value": "v143,host=x64,version=14",
                    "strategy": "external"
                },
                "architecture": {
                    "value": "x64",
                    "strategy": "external"
                },
                "inherits": f"default-{str(settings.os).lower()}-configuration"
            })
            
            presets["buildPresets"].append({
                "name": f"{compiler}{compiler_version}@{arch}_{build_type}_build",
                "configurePreset": f"{compiler}{compiler_version}@{arch}",
                "buildType": f"{build_type}"
            })
            
            presets["testPresets"].append({
                "name": f"{compiler}{compiler_version}@{arch}_{build_type}_test",
                "configurePreset": f"{compiler}{compiler_version}@{arch}",
                "buildPreset": f"{compiler}{compiler_version}@{arch}_{build_type}_build"
            })
            with open(presets_path, "w") as f:
                json.dump(presets, f, indent=4)
                
                
def handle_package(build_folder, package_folder, settings):
    rm(pattern="*.bat", folder=build_folder)
    rm(pattern="*.sh", folder=build_folder)
    rm(pattern="*.cmake", folder=build_folder)
    
    compiler = settings.compiler
    compiler_version = settings.compiler.version
    arch = settings.arch
    build_type = settings.build_type

    install_path = os.path.join(build_folder, "out", "install", f"{compiler}{compiler_version}@{arch}", build_type)
    if os.path.isdir(install_path):
        copy(pattern="*", dst=package_folder, src=install_path)
    else:
        copy(pattern="*", dst=package_folder, src=build_folder)
