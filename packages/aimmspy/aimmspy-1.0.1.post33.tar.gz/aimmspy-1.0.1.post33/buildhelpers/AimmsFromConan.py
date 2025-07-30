import os
import os
import sys
import shutil
import subprocess
import pathlib, fnmatch
import json
buildhelpersDir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(buildhelpersDir)
from . import gitinfo


class AimmsFromConan:

    def __init__(self, profile, version = "", getWrappers=True):
        self._isOnGitlab =  os.getenv("CI", False)
        self._setVersionAndPackageName(version)
        self._isWindows = (os.name!="posix") #current machine that is running the script
        self._isWinPackage = (profile[0:2] == "vc") if (profile != "") else self._isWindows #PRO linux package can be built on a windows machine
        self._profile = profile if (profile != "") else "vc141/debug" if self._isWindows else  "gcc61/debug" 
        self._toolset = self._getToolset()
        self._buildhelperspath = buildhelpersDir
        self._libbin = "bin" if self._isWinPackage else "lib"
        self._getWrappers = getWrappers
        self._CmlAndWFMSupportIncluded = False
        # setup conan
        cmdLine = "conan remote add conan-intra http://conan.intra.aimms.com:9300 False --insert 0"
        self._executeCmd(cmdLine, False)
        cmdLine = "conan config set general.parallel_download=4"
        self._executeCmd(cmdLine)


    def _setVersionAndPackageName(self, version):
        if version == "": 
            gi = gitinfo.gitinfo(warnVersion=False)
            version = gi.getVersion()
        self._packageChannel = "stable"
        self._version = version
        self._conanPackageName = f"{version}@aimms/{self._packageChannel}" #package name is like 4.84.51239.6@aimms/feature

    def setProfile(self, profile):
        self._profile = profile  # profile like vc141/release       
    
    def createAndPushYabrPackage(self):
        if self._isOnGitlab:
            buildtoolpath = os.path.join(buildhelpersDir,"..","..")
            sys.path.append(buildtoolpath)
            from buildtool.url import uri_exists
            from buildtool.yabr import yabr_archive_uri
            aimmsversion = gitinfo.gitinfo("engine").getVersion()
            print(("Checking for aimms version " + aimmsversion))
            os.environ["label"] = self._profile.partition('/')[0]
            os.environ["arch"] = "x64"
            os.environ["config"] = "Release" if (self._profile.partition('/')[2] == "release") else "Debug"
            uri_local = yabr_archive_uri("internal/com.aimms/aimms", aimmsversion)
            if uri_exists(uri_local) :
                print (f"Build artifact {uri_local} already exists (in Yabr repository).")
                sys.exit(0)
            print(("Not found " + uri_local))
        else: print("Not on Gitlab, not checking if yabr already exists")
        print(f"Creating Yabr package for Conan: {self._conanPackageName}")
        topath = os.path.join('target', self._toolset)
        self.installAimmsAndCopyTo(topath,CmlAndWFMSupportIncluded = True)
        self._yabrPush(self._toolset, "yabr.xml")
        print(f"Yabr package done")
    
    #copies files in a way similar to yabr package
    def installAimmsAndCopyTo(self, relativePath, CmlAndWFMSupportIncluded = False):
        print(f"Install Aimms: {self._conanPackageName} and corresponding Wrappers")
        self._CmlAndWFMSupportIncluded = CmlAndWFMSupportIncluded
        if CmlAndWFMSupportIncluded and os.path.exists(relativePath):  #when building IFA the folder should stay, because there is already some stuff in it
            shutil.rmtree(relativePath)
            self._createDirectory(relativePath)       

        if self._isWinPackage and self._getWrappers:
            self._wrapperAInstalledPackages = self._conanInstall(f"aimmsdllWrapperA/{self._conanPackageName}")
            self._wrapperWInstalledPackages = self._conanInstall(f"aimmsdllWrapperW/{self._conanPackageName}")
        
        aimmsInstalledPackages = self._conanInstall(f"aimms/{self._conanPackageName}")
        self._aimmsPath, tail = os.path.split(aimmsInstalledPackages["deps_env_info"]["PATH"][0])
        self._aimmsDependencies = aimmsInstalledPackages["dependencies"]

        print(f"Copy files to {relativePath}")
        self._copyAimmsFilesFromJson(relativePath)


    def _getRootPathForPackage(self, installedPackages, packageName):
            packageInfo = next(pkg for pkg in installedPackages if pkg["name"] == packageName)
            return packageInfo["rootpath"]
            

    def _conanInstall(self, package):
        print(f"Installing conan Aimms package {package}")
        prOpt = self._getProfileOption()
        cmdLine = f"conan install {package} -g json {prOpt}"
        self._executeCmd(cmdLine)

        with open("conanbuildinfo.json") as conanInstalledInfoFile:
            installedInfo = json.load(conanInstalledInfoFile)
            return installedInfo
    
    def _copyAimmsFilesFromJson(self, topath):
        shutil.copytree(src=f"{self._aimmsPath}/Modules", dst=f"{topath}/Modules")             
        solverspath = self._getRootPathForPackage(self._aimmsDependencies, "solvers")       
        self._copySolvers(solverspath, topath)
        shutil.copytree(src=f"{self._aimmsPath}/bin", dst=f"{topath}/Bin")               
        self._copy_dir(f"{self._aimmsPath}/misc", f"{topath}/Bin", "*")
        self._copy_dir(f"{self._aimmsPath}/include", f"{topath}/Api", "aimmsapi.h")            
        self._copySecurityBinaries(topath)
        if self._isWinPackage:
            if self._CmlAndWFMSupportIncluded: # WFMSupport not included in IFA, but only in Yabr package
                self._move_dir(f"{topath}/Bin", f"{topath}/WFMSupport", "aimmslic*")
            else:
                self._remove_dir(f"{topath}/Bin", "aimmslic*")
            shutil.copytree(src=f"{self._aimmsPath}/Templates", dst=f"{topath}/Templates")
            shutil.copytree(src=f"{self._aimmsPath}/Snippets", dst=f"{topath}/Snippets")
            
            if self._getWrappers:
                wrapperAbinpath = self._wrapperAInstalledPackages["deps_env_info"]["PATH"][0]
                wrapperWbinpath = self._wrapperWInstalledPackages["deps_env_info"]["PATH"][0]        
                self._copy_dir(f"{wrapperAbinpath}", f"{topath}/Api/Adapter/CHAR", "*")
                self._copy_dir(f"{wrapperWbinpath}", f"{topath}/Api/Adapter/WCHAR", "*")
                
            self._copy_dir(f"{self._aimmsPath}/lib", f"{topath}/Api", "*aimms3.lib")
            self._copy_dir(f"{solverspath}/include/lpd", f"{topath}/Api/OSI", "IAimmsOSI.h")
            self._copy_dir(f"{solverspath}/include/lpd", f"{topath}/Api/OSI", "aimmsosi_compat.h")
            self._copyLibs(topath, ('cppunit', 'autolib', 'dbms', 'log4cxx', 'modelparser', 'net4cxx', 'net4cxx-dev', 'security', 'servicelocator', 'beastweb', 'webclient', 'common', 'expat', 'atlmfc', 'dfsuni'))
        else:           
            self._copy_dir(f"{self._aimmsPath}/lib", f"{topath}/Bin", "*")
            self._copyLibs(topath, ('cppunit', 'autolib', 'dbms', 'log4cxx', 'modelparser', 'net4cxx', 'net4cxx-dev', 'security', 'servicelocator', 'beastweb', 'webclient', 'common', 'lzma', 'sodium', 'cryptopp'))
        self._cleanupBinFolder(topath)
    
    def _copySecurityBinaries(self, path):
        securitylibPath = self._getRootPathForPackage(self._aimmsDependencies, "security")
        if self._isWinPackage:
            shutil.copy(src=f"{securitylibPath}/bin/Config/UserDistinction.cfg", dst=f"{path}/Bin/UserDistinction.cfg")
        else:
            shutil.copy(src=f"{securitylibPath}/bin/DriveID", dst=f"{path}/Bin/DriveID")
            shutil.copy(src=f"{securitylibPath}/bin/NodelockTool", dst=f"{path}/Bin/NodelockTool")


    def _copySolvers(self, solverspath, topath):
        solverspath = self._getRootPathForPackage(self._aimmsDependencies, "solvers")       
        dynamicLibPattern = "*.so*" if not self._isWinPackage else "*.dll"
        self._copy_dir(f"{solverspath}/{self._libbin}", f"{topath}/Solvers", dynamicLibPattern)
        self._copy_dir(f"{solverspath}/{self._libbin}", f"{topath}/Solvers", "*.pdb")
        solverGroupNames = [ "conopt", "copt", "cplex", "gurobi", "knitro", "odh" ] if self._profile[-1]=='g' else [ "conopt", "copt", "cplex", "gurobi", "knitro", "odh", "octeract" ] #octeract only in release
        solverDirectories = [ "path47", "xa16" ] + [ dirName for group in solverGroupNames for dirName in self._listDirectories(f"{group}*") ]
        if self._isWinPackage: 
            solverDirectories += [ "baron21", "ipopt311" ] # Baron only exists on windows, ipopt is a shared lib on windows
        else:
            solverDirectories += [ "solversUtils" ] # solversUtils is empty on windows
        for dirName in solverDirectories:
            directory = self._getRootPathForPackage(self._aimmsDependencies, dirName)
            self._copy_dir(f"{directory}/lib", f"{topath}/Solvers", dynamicLibPattern) # Note: external-solvers don't do the bin/lib switch between win/linux
            if self._isWinPackage:
                self._copy_dir(f"{directory}/lib", f"{topath}/Solvers", "*.exe")
                self._copy_dir(f"{directory}/lib", f"{topath}/Solvers", "*.pdb")


    def _cleanupBinFolder(self, topath):
        if not self._CmlAndWFMSupportIncluded:
            self._remove_dir(f"{topath}/Bin", "cml*") #cml is not shipped
            self._remove_dir(f"{topath}/Bin", "api_test*")  
        self._remove_dir(f"{topath}/Bin", "*.a")  
        self._remove_dir(f"{topath}/Bin/Startpage/static/img", "*.jpg")

                
    def _listDirectories(self, pattern):
        directories = [ directory["name"] for directory in self._aimmsDependencies ]
        return fnmatch.filter(directories, pattern)
        

    def _copyLibs(self, path, libsList):    
        libsFilterDict = {
        'expat'     : "libexpatw.dll",
        'log4cxx'   : "*"  if self._isWinPackage else "*.so.10",
        'cppunit'   : "*"  if self._isWinPackage else "*.so.1",
        'sodium'    : "*"  if self._isWinPackage else "*.so.4",
        'cryptopp'  : "*"  if self._isWinPackage else "*.so.8",
        }
    
        for libName in libsList:
            libsfilter  =  "*" if self._isWinPackage else "*.so*"
            l = self._getRootPathForPackage(self._aimmsDependencies, libName)
            if libName in libsFilterDict : 
                libsfilter = libsFilterDict[libName] #some lib have specific filters
            self._copy_dir(f"{l}/{self._libbin}/", f"{path}/Bin", libsfilter)
       
        
    def _yabrPush(self, toolset, yabrFileName):
        if self._isOnGitlab:
            myenv = os.environ.copy()
            myenv["PROJECT_VERSION"] = gitinfo.gitinfo("engine").getVersion()
            ext = "bat" if self._isWinPackage else "sh"
            buildtoolpath = os.path.join(buildhelpersDir,"..","..")
            yabrScript = os.path.join(buildtoolpath,"buildtool", f'yabr.{ext}')
            cmd = f"{yabrScript} -yabr {yabrFileName} -toolset {toolset} push"
            print(cmd, flush=True)
            retCode = subprocess.call(cmd, shell=True, env = myenv )
            if retCode != 0:
                sys.exit(retCode)
            return retCode
        else: print("Not on Gitlab, not pushing yabr")

    @staticmethod
    def _move_dir(src: str, dst: str, pattern: str = '*'):
        if not os.path.isdir(dst):
            pathlib.Path(dst).mkdir(parents=True, exist_ok=True)
        for f in fnmatch.filter(os.listdir(src), pattern):
            if not os.path.isdir(f): shutil.move(os.path.join(src, f), os.path.join(dst, f))
        if pattern == '*': shutil.rmtree(src)

    @staticmethod
    def _remove_dir(src: str, pattern: str = '*'):
        if os.path.exists(src):
            if pattern == '*': shutil.rmtree(src)
            else: 
                for f in fnmatch.filter(os.listdir(src), pattern): os.remove(os.path.join(src, f))

    @staticmethod
    def _copy_dir(src: str, dst: str, pattern: str = '*'):
        if not os.path.isdir(dst):
            pathlib.Path(dst).mkdir(parents=True, exist_ok=True)
        for f in fnmatch.filter(os.listdir(src), pattern):
            if not os.path.isdir(os.path.join(src, f)): shutil.copy(os.path.join(src, f), os.path.join(dst, f))
                
    def _getToolset(self):
        label, delimeter, config = self._profile.partition('/')
        config = "Release" if (config == "release") else "Debug"
        return f"{label}_x64_{config}"   
    
    def _getProfileOption(self):
        profile = ""
        if len(self._profile) > 0:
            profile = "%s/conan-profiles/%s" %(self._buildhelperspath, self._profile)
            if not(os.path.isfile(profile)):
                print("profile %s not found" %self._profile)
                print("was looking for: %s" %profile)
                sys.exit(1)
            return f"-pr {profile}"
        return profile

    @staticmethod
    def _createDirectory(path):
        try: os.makedirs(path) 
        except OSError as err: os._exit(err.errno)
        print (f"Successfully created directory {path}")

    @staticmethod
    def _executeCmd(_cmdLine, exitOnFail=True):
        print(_cmdLine, flush=True)
        retCode = subprocess.call(_cmdLine, shell=True)
        if exitOnFail and retCode != 0:
            sys.exit(retCode)
        return retCode






