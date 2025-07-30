
import sys
import os

from conan import ConanFile

sys.path.append(os.path.join(os.getcwd(), "../../buildhelpers"))

class LatestAimmsCollectorConan(ConanFile):
    license = "AIMMS"
    author = "developers@aimms.com"
    url = "https://gitlab.aimms.com/aimms/aimms"
    description = "generated"
    topics = ("deployment only")
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeDeps"
    package_type = "application"

    def requirements(self):
        
        branch = os.getenv("AIMMS_TEST_BRANCH", "develop")
        version = os.getenv("AIMMS_TEST_VERSION")

        self.requires(f"aimms/{version}@aimms/{branch}")
