import os
import sys
from conan import ConanFile
from conan.tools.files import collect_libs, copy, rm


class aimmsAPIPyConan(ConanFile):
    license = "AIMMS"
    author = "developers@aimms.com"
    url = "https://gitlab.aimms.com/aimms/aimms"
    description = "engine"
    topics = ("Aimms engine")
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeDeps"
    package_type = "application"
    # revision_mode = "scm"

    requires = [
        "aimmsifc/0.2.0-11@aimms/master",
        "pybind11/2.13.6",
    ]

    test_requires = [
        "gtest_injector/1.5.2-16@aimms/main",
    ]

    tool_requires = [ 
    ]

    def requirements(self):
        self.requires("log4cxx/0.12.2-6@aimms25/main",transitive_headers=True, transitive_libs=True)
        self.requires("boost/1.86.0", force=True)

    def package(self):
        rm(self, "*.bat", self.build_folder)
        rm(self, "*.sh", self.build_folder)
        rm(self, "*.cmake", self.build_folder)

        copy(self, "*", dst=self.package_folder, src=self.build_folder)

    def package_info(self):
        pass
