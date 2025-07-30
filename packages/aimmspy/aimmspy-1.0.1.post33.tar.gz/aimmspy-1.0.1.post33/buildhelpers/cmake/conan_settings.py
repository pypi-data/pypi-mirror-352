def get_conan_settings(preset):
    preset_to_conan_settings = {
        "vc143@x86_64": {
            "arch": "x86_64",
            "compiler": "msvc",
            "compiler.version": "193",
        },
        "gcc11@x86_64": {
            "arch": "x86_64",
            "compiler": "gcc",
            "compiler.version": "11",
        }
    }

    return preset_to_conan_settings[preset]
