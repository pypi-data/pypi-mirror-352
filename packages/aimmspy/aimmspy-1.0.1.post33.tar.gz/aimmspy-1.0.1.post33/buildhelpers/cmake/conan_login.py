from aimms_common import executeCmd
import os
import subprocess


def login():
    conan_username = os.getenv('ARTIFACTORY_USERNAME')
    if conan_username is None:
        raise Exception(
            "Environment variable ARTIFACTORY_USERNAME is not set")

    conan_password = os.getenv('ARTIFACTORY_PASSWORD')
    if conan_password is None:
        raise Exception(
            "Environment variable ARTIFACTORY_PASSWORD is not set")

    executeCmd(f"conan remote login -p {conan_password} conan-intra {conan_username}")
    

if __name__ == '__main__':
    login()
