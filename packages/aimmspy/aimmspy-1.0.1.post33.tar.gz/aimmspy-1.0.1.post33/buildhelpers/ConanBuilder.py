import sys
import os
import subprocess
import logging
import argparse
import shutil
import traceback

from . import gitinfo
from . import ProductVersionEnvVars

def printenv(logger):
    if logger.isEnabledFor(logging.DEBUG):
        for k, v in os.environ.items():
            logger.debug('%s = %s' % (k, v))


def executeCmd(_cmdLine, exitOnFail=True):
    print(_cmdLine, flush=True)
    retCode = subprocess.call(_cmdLine, shell=True)
    if exitOnFail and retCode != 0:
        sys.exit(retCode)
    return retCode


class ConanAimmsServerConfig(object):
    def __init__(self):
        self.conan_username = os.getenv('CICD_CONAN_USERNAME', "")
        self.conan_password = os.getenv('CICD_CONAN_PASSWORD',"")

    def authenticate(self):
        # make sure we're authenticated
        if(self.conan_username == "" ):
            print("Conan User name was not provided, needed to authenticate, which is needed to access conan remote repo")
            sys.exit(1)
        cmdLine = "conan user -p %s -r conan-intra %s" % (self.conan_password, self.conan_username)
        executeCmd(cmdLine)


class ConanBuilder(object):
    def _getIsLocalArgument(self):
        parser = argparse.ArgumentParser(description='Conan build helper')
        parser.add_argument('--local', help='Use a local install dir and make the package editable', action='store_true')
        args = parser.parse_args()
        return args.local

    def __init__(self, loglevel="INFO", gitInfoLocation=None):
        self.logger = logging.getLogger("ConanBuilder")
        self.logger.setLevel(loglevel)
        printenv(self.logger)
        self.profile = self._getFromEnv("profile", "", True, True)
        self.isOnGitlab = self._getFromEnv("CI", False)
        self.gi = gitinfo.gitinfo(warnVersion=False, location=gitInfoLocation)
        self.fullyqualifiedpackagename = ""
        self._ensureConanIntraRemoteExists()
        self._setConanParallelDownloadNumOfThreads(4)
        self.ccf = ConanAimmsServerConfig()
        self.isLocal = self._getIsLocalArgument()
        # Cancelling a build can sometimes leave the conan locks in place
        # Forcefully removing them on the build agents helps prevent the runner
        # from hanging
        if self.isOnGitlab:
            self._forceReleaseConanLocks()

    def _forceReleaseConanLocks(self):
        executeCmd("conan remove --locks")

    def _getFromEnv(self, key, default, pop=False, lower=False):
        if pop:
            ret = os.environ.pop(key, default)
        else:
            ret = os.getenv(key, default)
        if lower:
            ret = ret.lower()
        self.logger.debug("%s: %s" % (key, ret))
        return ret

    def setProductEnv(self):
        # set the product version environment variables for use in
        # buildscripts down the line
        ev = ProductVersionEnvVars.ProductVersionEnvVars()
        ev.setMajor("%d" % self.gi.getMajor())
        ev.setMinor("%d" % self.gi.getMinor())
        ev.setRelease("%d" % self.gi.getRelease())
        ev.setRevision("%d" % self.gi.getRevision())
        ev.setHash(self.gi.getHash())
        ev.setBranchType(self.gi.getBranchType())

    def getVersion(self, UseConanRevision):
        # See https://docs.conan.io/en/latest/versioning/revisions.html
        # if using conan-revision, do not add the revision part to the version
        # so a consumer will automatically use the latest revision of the release
        if UseConanRevision :
            return "%d.%d.%d" % (self.gi.getMajor(), self.gi.getMinor(), self.gi.getRelease())
        else :
            return self.gi.getVersion()

    def _initFullyQualifiedPackageName(self, packageCompany, packageName, UseConanRevision = False, Channel = ""):
        # conan packages have the convention to be named:
        # packageName/packageVersion@packageCompany/packageChannel
        # adjust package details for conan
        packageVersion = self.getVersion(UseConanRevision)
        packageChannel = Channel
        if packageChannel == "":
            packageChannel = self.gi.getBranchType()
        self.fullyqualifiedpackagename = "%s/%s@%s/%s" % (packageName, packageVersion, packageCompany, packageChannel)

    def createPackage(self, packageCompany, packageName, UseConanRevision = False, Channel = ""):
        if not self.isLocal:
            return self.create(packageCompany, packageName, UseConanRevision, Channel)
        else:
            isReleaseBuild = self.profile.endswith("release")
            installFolder = "conan_build_release/build" if isReleaseBuild else "conan_build_debug/build"
            packageFolder = "conan_build_release/package" if isReleaseBuild else "conan_build_debug/package"
            self.install(installFolder)
            self.build(installFolder)
            self.package(installFolder, packageFolder)
            self.editable(packageFolder, packageCompany, packageName, UseConanRevision, Channel)
            return True


    def create(self, packageCompany, packageName, UseConanRevision = False, Channel = ""):
        self._initFullyQualifiedPackageName(packageCompany, packageName, UseConanRevision, Channel)
        if self.isOnGitlab:
            self.ccf.authenticate()
        if not self.isOnGitlab or not self._attemptPackageInstallFromRemote():
            profileOption = self._getProfileOption()
            createArgs = os.getenv("CONAN_CREATE_ARGUMENTS", "")
            cmdLine = f"conan create . {self.fullyqualifiedpackagename} {profileOption} {self.forceupdate} {createArgs}"
            executeCmd(cmdLine)
            return True
        return False

    def install(self, installFolder):
        if self.isOnGitlab:
            self.ccf.authenticate()
        profileOption = self._getProfileOption()
        executeCmd(f"conan install . --install-folder {installFolder} {profileOption}")

    def build(self, installFolder):
        executeCmd(f"conan build . --build-folder {installFolder}")

    def package(self, installFolder, packageFolder):
        executeCmd(f"conan package --build-folder {installFolder} --package-folder {packageFolder} .")

    def editable(self, packageFolder, packageCompany, packageName, UseConanRevision, Channel):
        shutil.copy("conanfile.py", packageFolder) # Conan demands a directory with conanfile, bin, lib, public structure
        self._initFullyQualifiedPackageName(packageCompany, packageName, UseConanRevision, Channel)
        executeCmd(f"conan editable add {packageFolder} {self.fullyqualifiedpackagename}")

    @property
    def forceupdate(self):
        doupdate = os.getenv("CONAN_DO_UPDATE", "False") == "True"
        if doupdate:
           return "--update"
        else:
            return  ""

    def upload(self, forced=False):
        # the buildmachines will complain that the recipe time stamp is too old, that is because we are uploading the recipe in each job
        # and the date of the recipe repo is than compared to what the other job has just uploaded,
        # with forced=True this will not become an error, so you probably need this
        if self.isOnGitlab:
            if self.fullyqualifiedpackagename == "":
                self.logger.error("attempt to upload %s without creating it" % self.fullyqualifiedpackagename)
                traceback.print_exc()
                sys.exit(1)
            self.ccf.authenticate()
            force = ""
            if forced:
                force = "--force"

            cmdLine = "conan upload %s --all %s  -r conan-intra" % (self.fullyqualifiedpackagename, force)
            executeCmd(cmdLine)

        else:
            print("Not uploading because not on Gitlab.")

    def __del__(self):
        # clean up temporary stuff
        if self.fullyqualifiedpackagename != "":
            cmdLine = f'conan remove {self.fullyqualifiedpackagename} -s -b -f'
            executeCmd(cmdLine)

    def _getProfileOption(self):
        profile = ""
        if len(self.profile) > 0:
            profile = "%s/conan-profiles/%s" %(os.path.dirname(os.path.realpath(__file__)), self.profile)
            if not(os.path.isfile(profile)):
                print("profile %s not found" %self.profile)
                print("was looking for: %s" %profile)
                sys.exit(1)
            return f"-pr {profile}"
        return profile

    def _attemptPackageInstallFromRemote(self):
        profileOption = self._getProfileOption()
        retCode = executeCmd(f'conan install {self.fullyqualifiedpackagename} {profileOption}', exitOnFail=False)
        return retCode == 0

    def _ensureConanIntraRemoteExists(self):
        # processResult = subprocess.run(['conan', 'remote', "list"], stdout=subprocess.PIPE)
        # processOutput = processResult.stdout.decode('utf-8')
        # if not "conan-intra" in processOutput:
            # executeCmd("conan remote add conan-intra http://conan.intra.aimms.com:9300 False --insert 0")
        pass
            
    def _setConanParallelDownloadNumOfThreads(self, numOfThreads):
        executeCmd(f"conan config set general.parallel_download={numOfThreads}")